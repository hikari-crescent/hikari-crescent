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
    TypeVar,
    Union,
)

from hikari import Message, PartialChannel, Role, User

if TYPE_CHECKING:
    from crescent.commands.hooks import HookResult
    from crescent.context import Context
    from crescent.mentionable import Mentionable

__all__: Sequence[str] = (
    "CommandCallbackT",
    "OptionTypesT",
    "UserCommandCallbackT",
    "MessageCommandCallbackT",
    "CommandOptionsT",
    "ClassCommandProto",
    "HookCallbackT",
    "ErrorHandlerCallbackT",
)

CommandCallbackT = Callable[..., Awaitable[Any]]
UserCommandCallbackT = Union[
    Callable[["Context", User], Awaitable[None]],
    Callable[[Any, "Context", User], Awaitable[None]],
]
MessageCommandCallbackT = Union[
    Callable[["Context", Message], Awaitable[None]],
    Callable[[Any, "Context", Message], Awaitable[None]],
]

OptionTypesT = Union[str, bool, int, float, PartialChannel, Role, User, "Mentionable"]
CommandOptionsT = Dict[str, Union[OptionTypesT, User, Message]]
HookCallbackT = Callable[["Context"], Awaitable[Optional["HookResult"]]]


class ClassCommandProto(Protocol):
    async def callback(self, ctx: Context) -> Any:
        ...


ERROR = TypeVar("ERROR", bound=Exception, contravariant=True)

ErrorHandlerCallbackT = Union[
    Callable[[ERROR, "Context"], Awaitable[None]],
    Callable[[Any, ERROR, "Context"], Awaitable[None]],
]
