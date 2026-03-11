from __future__ import annotations

from hikari import ChannelType, OptionType

from crescent import command, options


def test_option_types():
    @command(name="all-option-types")
    class AllOptionTypes:
        text = options.string("text")
        integer = options.number("integer")
        boolean = options.boolean("boolean")
        number = options.floating("number")
        user = options.user("user")
        role = options.role("role")
        mentionable = options.mentionable("mentionable")
        channel = options.channel("channel")
        channel_list = options.channel("channel list").channel_types(
            [ChannelType.GUILD_TEXT, ChannelType.GUILD_VOICE]
        )
        attachment = options.attachment("attachment")

        async def callback(self, ctx): ...

    command_options = AllOptionTypes.metadata.app_command.options

    assert command_options

    assert command_options[0].type == OptionType.STRING
    assert command_options[1].type == OptionType.INTEGER
    assert command_options[2].type == OptionType.BOOLEAN
    assert command_options[3].type == OptionType.FLOAT
    assert command_options[4].type == OptionType.USER
    assert command_options[5].type == OptionType.ROLE
    assert command_options[6].type == OptionType.MENTIONABLE
    assert command_options[7].type == OptionType.CHANNEL
    assert command_options[8].type == OptionType.CHANNEL
    assert command_options[9].type == OptionType.ATTACHMENT


def test_string_length_limits():
    @command(name="string-length-limits")
    class StringLengthLimits:
        value = options.string("value").min_length(2).max_length(4)

        async def callback(self, ctx): ...

    command_options = StringLengthLimits.metadata.app_command.options

    assert command_options
    assert command_options[0].min_length == 2
    assert command_options[0].max_length == 4
    assert command_options[0].min_value is None
    assert command_options[0].max_value is None
