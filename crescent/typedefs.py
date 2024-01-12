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
from hikari.api import EntityFactory

if TYPE_CHECKING:
    from crescent.commands.hooks import HookResult
    from crescent.context import AutocompleteContext, Context
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
    "AutocompleteValueT",
)

CommandCallbackT = Callable[["Context"], Awaitable[Any]]
UserCommandCallbackT = Callable[["Context", User], Awaitable[None]]
MessageCommandCallbackT = Callable[["Context", Message], Awaitable[None]]

OptionTypesT = Union[str, bool, int, float, PartialChannel, Role, User, "Mentionable", Attachment]
CommandOptionsT = Dict[str, Union[OptionTypesT, User, Message]]
HookCallbackT = Callable[["Context"], Awaitable[Optional["HookResult"]]]
AutocompleteValueT = TypeVar("AutocompleteValueT", str, int, float)
AutocompleteCallbackT = Callable[
    ["AutocompleteContext", AutocompleteInteractionOption],
    Awaitable[Sequence[Tuple[str, AutocompleteValueT]]],
]

PluginCallbackT = Callable[[], None]


class ClassCommandProto(Protocol):
    """A type with all the attributes required for class commands."""

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
