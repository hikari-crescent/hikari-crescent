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
    Tuple,
    TypeVar,
    Union,
)

from hikari import (
    Attachment,
    AutocompleteInteractionOption,
    Event,
    Message,
    PartialChannel,
    Role,
    User,
)

if TYPE_CHECKING:
    from crescent.context import AutocompleteContext, Context
    from crescent.hooks import HookResult
    from crescent.mentionable import Mentionable

__all__: Sequence[str] = (
    "CommandCallbackT",
    "OptionTypesT",
    "UserCommandCallbackT",
    "MessageCommandCallbackT",
    "CommandOptionsT",
    "ClassCommandProto",
    "CommandErrorHandlerCallbackT",
    "AutocompleteCallbackT",
    "AutocompleteValueT",
    "CommandHookCallbackT",
    "EventHookCallbackT",
)

CommandCallbackT = Callable[["Context"], Awaitable[Any]]
UserCommandCallbackT = Callable[["Context", User], Awaitable[None]]
MessageCommandCallbackT = Callable[["Context", Message], Awaitable[None]]

OptionTypesT = Union[str, bool, int, float, PartialChannel, Role, User, "Mentionable", Attachment]
CommandOptionsT = Dict[str, Union[OptionTypesT, User, Message]]
AutocompleteValueT = TypeVar("AutocompleteValueT", str, int, float)
AutocompleteCallbackT = Callable[
    ["AutocompleteContext", AutocompleteInteractionOption],
    Awaitable[Sequence[Tuple[str, AutocompleteValueT]]],
]

CommandHookCallbackT = Callable[["Context"], Awaitable[Optional["HookResult"]]]

EventT = TypeVar("EventT", bound=Event)
EventHookCallbackT = Callable[["EventT"], Awaitable[Optional["HookResult"]]]

PluginCallbackT = Callable[[], None]


class ClassCommandProto(Protocol):
    """A type with all the attributes required for class commands."""

    async def callback(self, ctx: Any) -> Any: ...


ErrorT = TypeVar("ErrorT", bound=Exception, contravariant=True)

CommandErrorHandlerCallbackT = Callable[[ErrorT, Any], Awaitable[None]]
EventErrorHandlerCallbackT = Callable[[ErrorT, Event], Awaitable[None]]
AutocompleteErrorHandlerCallbackT = Callable[
    [ErrorT, Any, AutocompleteInteractionOption], Awaitable[None]
]
