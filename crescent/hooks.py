from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, Sequence, TypeVar, overload

from hikari import Event

from crescent.events import EventMeta
from crescent.internal.app_command import AppCommandMeta

if TYPE_CHECKING:
    from crescent.internal.includable import Includable
    from crescent.typedefs import CommandHookCallbackT, EventHookCallbackT

IncludableT = TypeVar("IncludableT")
EventT = TypeVar("EventT", bound=Event, contravariant=True)

__all__: Sequence[str] = ("HookResult", "hook")


@dataclass
class HookResult:
    """
    An object return by hooks to provide information about what to do after
    the hook is run.

    Args:
        exit: If true, don't run any following hooks or the command.
    """

    exit: bool = False


@overload
def hook(*callbacks: CommandHookCallbackT, after: bool = False) -> _Hook[AppCommandMeta]: ...


@overload
def hook(
    *callbacks: EventHookCallbackT[EventT], after: bool = False
) -> _Hook[EventMeta[EventT]]: ...


def hook(
    *callbacks: CommandHookCallbackT | EventHookCallbackT[EventT], after: bool = False
) -> _Hook[Any]:
    # TODO: Example for events
    """
    Register a hook to a command or event.

    ### Example
    ```python
    async def say_hi(ctx: crescent.Context) -> None:
        await ctx.respond("Hello there")

    @client.include
    @crescent.hook(say_hi)
    @crescent.command
    async def ping(ctx: crescent.Context):
        await ctx.respond("Pong")
    ```

    Args:
        after: If true, run this hook after the command or event has completed.
    """
    return _Hook(callbacks, after)


class _Hook(Generic[IncludableT]):
    def __init__(self, callbacks: Any, after: bool):
        self.callbacks = callbacks
        self.after = after

    @overload
    def __call__(
        self: _Hook[AppCommandMeta], obj: Includable[AppCommandMeta]
    ) -> Includable[AppCommandMeta]: ...

    @overload
    def __call__(
        self: _Hook[EventMeta[EventT]], obj: Includable[EventMeta[EventT]]
    ) -> Includable[EventMeta[EventT]]: ...

    def __call__(self, obj: Includable[Any]) -> Includable[Any]:
        if isinstance(obj.metadata, AppCommandMeta):
            obj.metadata.add_hooks(self.callbacks, prepend=True, after=self.after)
        elif isinstance(metadata := obj.metadata, EventMeta):
            metadata.add_hooks(self.callbacks, prepend=True, after=self.after)
        else:
            raise TypeError("Unsupported type, this should never happen.")

        return obj


def add_hooks(
    obj: Includable[Any],
    command_hooks: Sequence[CommandHookCallbackT],
    command_after_hooks: Sequence[CommandHookCallbackT],
    event_hooks: Sequence[EventHookCallbackT[Event]],
    event_after_hooks: Sequence[EventHookCallbackT[Event]],
) -> None:
    if isinstance(obj.metadata, AppCommandMeta):
        obj.metadata.add_hooks(command_hooks, after=False)
        obj.metadata.add_hooks(command_after_hooks, after=True)
    elif isinstance(metadata := obj.metadata, EventMeta):
        metadata.add_hooks(event_hooks, after=False)
        metadata.add_hooks(event_after_hooks, after=True)
