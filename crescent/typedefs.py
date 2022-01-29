from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Protocol, Sequence, Union

from hikari import PartialChannel, Role, User, Message

from crescent.commands.hooks import HookResult
from crescent.context import Context
from crescent.mentionable import Mentionable

__all__: Sequence[str] = (
    "CommandCallback",
    "CommandOptionsT",
    "ClassCommandProto",
    "HookCallbackT",
)

CommandCallback = Callable[..., Awaitable[Any]]
UserCommandCallbackT = Callable[[Context, User], Awaitable[None]]
MessageCommandCallbackT = Callable[[Context, Message], Awaitable[None]]
OptionTypesT = Union[str, bool, int, float, PartialChannel, Role, User, Mentionable]
CommandOptionsT = Dict[str, OptionTypesT]
HookCallbackT = Callable[[Context, CommandOptionsT], Awaitable[HookResult]]


class ClassCommandProto(Protocol):
    async def callback(self, ctx: Context) -> Any:
        ...
