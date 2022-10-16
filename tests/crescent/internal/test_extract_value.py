from __future__ import annotations

from typing import Optional

import attrs
from hikari import OptionType, ResolvedOptionData, Snowflake

from crescent.internal.handle_resp import _extract_value


@attrs.define
class MockInteraction:
    resolved: Optional[ResolvedOptionData]


@attrs.define
class MockOption:
    type: OptionType | str
    value: Snowflake | str | int | bool


def test_extract_str():
    command_interaction = MockInteraction(None)
    option = MockOption(type=OptionType.STRING, value="12345")

    assert _extract_value(option, command_interaction) == "12345"


def test_extract_user():
    USER = object()

    command_interaction = MockInteraction(
        resolved=ResolvedOptionData(
            users={"12345": USER}, members={}, roles={}, channels={}, messages={}, attachments={}
        )
    )
    option = MockOption(type=OptionType.USER, value="12345")

    assert _extract_value(option, command_interaction) is USER


def test_extract_channel():
    CHANNEL = object()

    command_interaction = MockInteraction(
        resolved=ResolvedOptionData(
            users={},
            members={},
            roles={},
            channels={"12345": CHANNEL},
            messages={},
            attachments={},
        )
    )
    option = MockOption(type=OptionType.CHANNEL, value="12345")

    assert _extract_value(option, command_interaction) is CHANNEL


def test_extract_attachment():
    ATTACHMENT = object()

    command_interaction = MockInteraction(
        resolved=ResolvedOptionData(
            users={},
            members={},
            roles={},
            channels={},
            messages={},
            attachments={"12345": ATTACHMENT},
        )
    )
    option = MockOption(type=OptionType.ATTACHMENT, value="12345")

    assert _extract_value(option, command_interaction) is ATTACHMENT


def test_extract_autocomplete_option():
    command_interaction = MockInteraction(None)
    option = MockOption(type=OptionType.USER, value=Snowflake(12345))

    assert _extract_value(option, command_interaction) == Snowflake(12345)
