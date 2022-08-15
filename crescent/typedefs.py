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

if TYPE_CHECKING:
    from crescent.commands.hooks import HookResult
    from crescent.context import AutocompleteContext, BaseContext
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
_TransformedHookCallbackT = Callable[
    [Any], Awaitable[Tuple[Optional["HookResult"], "BaseContext"]]
]
AutocompleteCallbackT = Callable[
    ["AutocompleteContext", AutocompleteInteractionOption], Awaitable[Sequence[CommandChoice]]
]

PluginCallbackT = Callable[[], None]


class ClassCommandProto(Protocol):
    async def callback(self, ctx: Any) -> Any:
        ...


ERROR = TypeVar("ERROR", bound=Exception, contravariant=True)

CommandErrorHandlerCallbackT = Callable[[ERROR, Any], Awaitable[None]]
EventErrorHandlerCallbackT = Callable[[ERROR, Event], Awaitable[None]]
AutocompleteErrorHandlerCallbackT = Callable[
    [ERROR, "AutocompleteContext", AutocompleteInteractionOption], Awaitable[None]
]
