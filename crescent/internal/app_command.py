from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING, Tuple

from attr import define
from hikari import CommandOption

if TYPE_CHECKING:
    from typing import Optional, Sequence
    from hikari import Snowflake

    Unique = Tuple[
        str,
        Optional[Snowflake],
        Optional[str],
        Optional[str]
    ]

__all__: Sequence[str] = (
    "AppCommandMeta",
    "AppCommand",
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
    options: Optional[Sequence[CommandOption]]
    default_permission: Optional[bool]

    id: Optional[Snowflake] = None


@define
class AppCommandMeta:
    app: AppCommand
    group: Optional[str] = None
    sub_group: Optional[str] = None

    @property
    def unique(self) -> Unique:
        return (
            self.app.name,
            self.app.guild_id,
            self.group,
            self.sub_group,
        )
