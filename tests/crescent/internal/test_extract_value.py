from __future__ import annotations

from typing import Optional

import attrs
from hikari import OptionType, ResolvedOptionData, Snowflake

from crescent.internal.handle_resp import _extract_value


@attrs.define
class MockInteraction:
    resolved: Optional[ResolvedOptionData]
    guild_id: int | None


@attrs.define
class MockOption:
    type: OptionType | str
    value: Snowflake | str | int | bool


def test_extract_str():
    command_interaction = MockInteraction(None, None)
    option = MockOption(type=OptionType.STRING, value="12345")

    assert _extract_value(option, command_interaction) == "12345"


def test_extract_user():
    USER = object()

    command_interaction = MockInteraction(
        resolved=ResolvedOptionData(
            users={"12345": USER}, members={}, roles={}, channels={}, messages={}, attachments={}
        ),
        guild_id=None,
    )
    option = MockOption(type=OptionType.USER, value="12345")

    assert _extract_value(option, command_interaction) is USER


def test_extract_member():
    MEMBER = object()

    command_interaction = MockInteraction(
        resolved=ResolvedOptionData(
            users={}, members={"12345": MEMBER}, roles={}, channels={}, messages={}, attachments={}
        ),
        guild_id=12345,
    )
    option = MockOption(type=OptionType.USER, value="12345")

    assert _extract_value(option, command_interaction) is MEMBER


def test_extract_autocomplete_option():
    command_interaction = MockInteraction(None, None)
    option = MockOption(type=OptionType.USER, value=Snowflake(12345))

    assert _extract_value(option, command_interaction) == Snowflake(12345)
