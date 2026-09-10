from __future__ import annotations

import pytest
from hikari.impl import EntityFactoryImpl

from crescent import command, message_command, options, user_command
from tests.utils import Locale, MockBot

WORDS = {
    "word": "word",
    "PascalCase": "pascal-case",
    "camelCase": "camel-case",
    "snake_case": "snake-case",
    "CAPSCase": "caps-case",
    "camelCAPSCase": "camel-caps-case",
    "SCREAMING_SNAKE_CASE": "screaming-snake-case",
    "what_ISThis": "what-is-this",
    "L2The3": "l2-the3",
    "already-kebab": "already-kebab",
}


@pytest.mark.parametrize(
    ("python_name", "expected"),
    ((k, v) for k, v in WORDS.items())
)
def test_shared_naming_rules(python_name, expected):
    async def callback(ctx, *args): ...

    callback.__name__ = python_name
    for decorator in (command, user_command, message_command):
        assert decorator(callback).metadata.app_command.name == expected

    class CommandClass:
        async def callback(self, ctx): ...

    CommandClass.__name__ = python_name
    assert command(CommandClass).metadata.app_command.name == expected
    assert options.String("An option")._gen_option(python_name).name == expected


@pytest.mark.parametrize("name", WORDS.keys())
def test_explicit_names_are_unchanged(name):
    async def my_command(ctx, *args): ...

    for decorator in (command, user_command, message_command):
        assert decorator(name=name)(my_command).metadata.app_command.name == name

    class MyCommand:
        async def callback(self, ctx): ...

    assert command(name=name)(MyCommand).metadata.app_command.name == name
    assert options.String("An option", name=name)._gen_option("my_option").name == name


def test_localized_names_are_unchanged():
    command_name = Locale("command_name", en_US="Command_Name")
    option_name = Locale("option_name", en_US="Option_Name")

    @command(name=command_name)
    class MyCommand:
        my_option = options.String("An option", name=option_name)

        async def callback(self, ctx): ...

    built = MyCommand.metadata.app_command.build(EntityFactoryImpl(MockBot()))
    assert built["name"] == "command_name"
    assert built["name_localizations"] == {"en-US": "Command_Name"}
    assert built["options"][0]["name"] == "option_name"
    assert built["options"][0]["name_localizations"] == {"en-US": "Option_Name"}


@pytest.mark.asyncio
@pytest.mark.parametrize("supply_default", [False, True])
async def test_option_names_map_to_original_attributes(supply_default):
    async def convert(value):
        return int(value)

    @command
    class MyCommand:
        my_option = options.String("An option")
        converted_value = options.String("A converted option", converter=int)
        async_value = options.String("An async converted option", converter=convert)
        default_value = options.String(
            "An optional value", default="fallback_value", converter=int
        )
        renamed_option = options.String("An explicitly named option", name="custom_name")

        async def callback(self, ctx):
            return (
                self.my_option,
                self.converted_value,
                self.async_value,
                self.default_value,
                self.renamed_option,
            )

    assert MyCommand.metadata.app_command.name == "my-command"
    assert (opts := MyCommand.metadata.app_command.options) is not None
    assert [option.name for option in opts] == [
        "my-option",
        "converted-value",
        "async-value",
        "default-value",
        "custom_name",
    ]

    values = {
        "my-option": "some_value",
        "converted-value": "12",
        "async-value": "34",
        "custom_name": "unchanged_value",
    }
    if supply_default:
        values["default-value"] = "56"

    result = await MyCommand.metadata.callback(None, **values)
    assert result == (
        "some_value",
        12,
        34,
        56 if supply_default else "fallback_value",
        "unchanged_value",
    )


def test_autocomplete_uses_generated_option_names():
    async def autocomplete(ctx, option):
        return []

    @command
    class MyCommand:
        my_option = options.String("An option", autocomplete=autocomplete)
        renamed_option = options.String(
            "An explicitly named option", name="custom_name", autocomplete=autocomplete
        )

        async def callback(self, ctx): ...

    assert MyCommand.metadata.autocomplete == {
        "my-option": autocomplete,
        "custom_name": autocomplete,
    }
    assert (opts := MyCommand.metadata.app_command.options) is not None
    assert all(option.autocomplete for option in opts)
