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
    CommandChoice,
    Event,
    Message,
    PartialChannel,
    Role,
    User,
)
from hikari.api import EntityFactory

if TYPE_CHECKING:
    from crescent.commands.hooks import HookResult
    from crescent.context import BaseContext
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
UserCommandCallbackT = Callable[[Any, User], Awaitable[None]]
MessageCommandCallbackT = Callable[[Any, Message], Awaitable[None]]

OptionTypesT = Union[str, bool, int, float, PartialChannel, Role, User, "Mentionable", Attachment]
CommandOptionsT = Dict[str, Union[OptionTypesT, User, Message]]
HookCallbackT = Callable[[Any], Awaitable[Optional["HookResult"]]]
TransformedHookCallbackT = Callable[[Any], Awaitable[Tuple[Optional["HookResult"], "BaseContext"]]]
AutocompleteCallbackT = Callable[
    [Any, AutocompleteInteractionOption], Awaitable[Sequence[CommandChoice]]
]
TransformedAutocompleteCallbackT = Callable[
    [Any, AutocompleteInteractionOption], Awaitable[Tuple[Sequence[CommandChoice], "BaseContext"]]
]

PluginCallbackT = Callable[[], None]


class ClassCommandProto(Protocol):
    async def callback(self, ctx: Any) -> Any:
        ...


ERROR = TypeVar("ERROR", bound=Exception, contravariant=True)

CommandErrorHandlerCallbackT = Callable[[ERROR, Any], Awaitable[None]]
EventErrorHandlerCallbackT = Callable[[ERROR, Event], Awaitable[None]]
AutocompleteErrorHandlerCallbackT = Callable[
    [ERROR, Any, AutocompleteInteractionOption], Awaitable[None]
]


class CanBuild(Protocol):
    def build(self, encoder: EntityFactory) -> dict[str, Any]:
        ...
