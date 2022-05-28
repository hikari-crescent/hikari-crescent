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

from hikari import (
    AutocompleteInteractionOption,
    CommandChoice,
    Message,
    PartialChannel,
    Role,
    User,
)

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
    "AutocompleteCallbackT",
)

CommandCallbackT = Callable[..., Awaitable[Any]]
UserCommandCallbackT = Callable[["Context", User], Awaitable[None]]
MessageCommandCallbackT = Callable[["Context", Message], Awaitable[None]]

OptionTypesT = Union[str, bool, int, float, PartialChannel, Role, User, "Mentionable"]
CommandOptionsT = Dict[str, Union[OptionTypesT, User, Message]]
HookCallbackT = Callable[["Context"], Awaitable[Optional["HookResult"]]]
AutocompleteCallbackT = Callable[
    ["Context", AutocompleteInteractionOption], Awaitable[Sequence[CommandChoice]]
]


class ClassCommandProto(Protocol):
    async def callback(self, ctx: Context) -> Any:
        ...


ERROR = TypeVar("ERROR", bound=Exception, contravariant=True)

ErrorHandlerCallbackT = Callable[[ERROR, "Context"], Awaitable[None]]
