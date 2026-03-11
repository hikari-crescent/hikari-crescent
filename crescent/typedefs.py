from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    Protocol,
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

__all__ = (
    "AutocompleteCallbackT",
    "AutocompleteValueT",
    "ClassCommandProto",
    "CommandCallbackT",
    "CommandErrorHandlerCallbackT",
    "CommandHookCallbackT",
    "CommandOptionsT",
    "EventHookCallbackT",
    "MessageCommandCallbackT",
    "OptionTypesT",
    "UserCommandCallbackT",
)

CommandCallbackT = Callable[["Context"], Awaitable[Any]]
UserCommandCallbackT = Callable[["Context", User], Awaitable[None]]
MessageCommandCallbackT = Callable[["Context", Message], Awaitable[None]]

OptionTypesT = Union[str, bool, int, float, PartialChannel, Role, User, "Mentionable", Attachment]
CommandOptionsT = dict[str, OptionTypesT | User | Message]
AutocompleteValueT = TypeVar("AutocompleteValueT", str, int, float)
AutocompleteCallbackT = Callable[
    ["AutocompleteContext", AutocompleteInteractionOption],
    Awaitable[Sequence[tuple[str, AutocompleteValueT]]],
]

CommandHookCallbackT = Callable[["Context"], Awaitable[Optional["HookResult"]]]

EventT = TypeVar("EventT", bound=Event)
EventHookCallbackT = Callable[["EventT"], Awaitable[Optional["HookResult"]]]

PluginCallbackT = Callable[[], None]


class ClassCommandProto(Protocol):
    """A type with all the attributes required for class commands."""

    async def callback(self, ctx: Any) -> Any: ...


ErrorT_contra = TypeVar("ErrorT_contra", bound=Exception, contravariant=True)

CommandErrorHandlerCallbackT = Callable[[ErrorT_contra, Any], Awaitable[None]]
EventErrorHandlerCallbackT = Callable[[ErrorT_contra, Event], Awaitable[None]]
AutocompleteErrorHandlerCallbackT = Callable[
    [ErrorT_contra, Any, AutocompleteInteractionOption],
    Awaitable[None],
]
