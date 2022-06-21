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
    Attachment,
    AutocompleteInteractionOption,
    CommandChoice,
    Event,
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
    "CommandErrorHandlerCallbackT",
    "AutocompleteCallbackT",
)

CommandCallbackT = Callable[..., Awaitable[Any]]
UserCommandCallbackT = Callable[["Context", User], Awaitable[None]]
MessageCommandCallbackT = Callable[["Context", Message], Awaitable[None]]

OptionTypesT = Union[str, bool, int, float, PartialChannel, Role, User, "Mentionable", Attachment]
CommandOptionsT = Dict[str, Union[OptionTypesT, User, Message]]
HookCallbackT = Callable[["Context"], Awaitable[Optional["HookResult"]]]
AutocompleteCallbackT = Callable[
    ["Context", AutocompleteInteractionOption], Awaitable[Sequence[CommandChoice]]
]

PluginCallbackT = Callable[[], None]


class ClassCommandProto(Protocol):
    async def callback(self, ctx: Context) -> Any:
        ...


ERROR = TypeVar("ERROR", bound=Exception, contravariant=True)

CommandErrorHandlerCallbackT = Callable[[ERROR, "Context"], Awaitable[None]]
EventErrorHandlerCallbackT = Callable[[ERROR, Event], Awaitable[None]]
AutocompleteErrorHandlerCallbackT = Callable[
    [ERROR, "Context", AutocompleteInteractionOption], Awaitable[None]
]
