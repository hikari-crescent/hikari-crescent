from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING

from attr import define
from hikari import ChannelType, OptionType

if TYPE_CHECKING:
    from typing import Optional, Sequence
    from hikari import Snowflake


__all__: Sequence[str] = (
    "AppCommandMeta",
    "AppCommand"
)


class AppCommandType(IntEnum):
    CHAT_INPUT = 1
    USER = 2
    MESSAGE = 3


@define
class AppCommand:
    """Local representation of an Application Command"""
    type: AppCommandType
    name: str
    description: str
    guild_id: Optional[Snowflake]
    options: Optional[Sequence[AppCommandOption]]
    default_permission: Optional[bool]


@define
class AppCommandOption:
    type: OptionType
    name: str
    description: str
    required: Optional[bool]
    choices: Optional[Sequence[Choice]]
    options: Optional[Sequence[AppCommandOption]]
    channel_types: Optional[Sequence[ChannelType]]
    min_value: Optional[int | float]
    max_value: Optional[int | float]
    autocomplete: Optional[bool]


@define
class Choice:
    name: str
    value: str | int | float


@define
class AppCommandMeta:
    app: AppCommand
    group: Optional[str] = None
    sub_group: Optional[str] = None

    @property
    def unique(self) -> int:
        return hash(
            (
                self.app.name,
                self.app.guild_id,
                self.group,
                self.sub_group,
            )
        )
