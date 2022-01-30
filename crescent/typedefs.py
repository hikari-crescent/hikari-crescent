from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Dict,
    Optional,
    Protocol,
    Sequence,
    Union,
)

from hikari import PartialChannel, Role, User, Message

if TYPE_CHECKING:
    from crescent.commands.hooks import HookResult
    from crescent.context import Context
    from crescent.mentionable import Mentionable

__all__: Sequence[str] = (
    "CommandCallback",
    "OptionTypesT",
    "UserCommandCallbackT",
    "MessageCommandCallbackT",
    "CommandOptionsT",
    "ClassCommandProto",
    "HookCallbackT",
)

CommandCallback = Callable[..., Awaitable[Any]]
OptionTypesT = Union[str, bool, int, float, PartialChannel, Role, User, "Mentionable"]
UserCommandCallbackT = Callable[["Context", User], Awaitable[None]]
MessageCommandCallbackT = Callable[["Context", Message], Awaitable[None]]
CommandOptionsT = Dict[str, Union[OptionTypesT, User, Message]]
HookCallbackT = Callable[["Context", CommandOptionsT], Awaitable[Optional["HookResult"]]]


class ClassCommandProto(Protocol):
    async def callback(self, ctx: Context) -> Any:
        ...
