from __future__ import annotations

from typing import Optional

from crescent.internal.handle_resp import _extract_value
from hikari import OptionType, ResolvedOptionData, Snowflake
import attrs


@attrs.define
class MockInteraction:
    resolved: Optional[ResolvedOptionData]


@attrs.define
class MockOption:
    type: OptionType | str
    value: Snowflake | str | int | bool


def test_extract_str():
    command_interaction = MockInteraction(None)

    option = MockOption(type=OptionType.USER, value=Snowflake(12345))

    assert _extract_value(option, command_interaction) == Snowflake(12345)
