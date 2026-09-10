from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, overload

from hikari import Event

from crescent.events import EventMeta
from crescent.internal.app_command import AppCommandMeta

if TYPE_CHECKING:
    from collections.abc import Sequence

    from crescent.internal.includable import Includable
    from crescent.typedefs import CommandHookCallbackT, EventHookCallbackT

__all__ = ("HookResult", "hook")


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
def hook[E: Event](
    *callbacks: EventHookCallbackT[E],
    after: bool = False,
) -> _Hook[EventMeta[E]]: ...


def hook[E: Event](
    *callbacks: CommandHookCallbackT | EventHookCallbackT[E],
    after: bool = False,
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
    return _Hook(callbacks, after=after)


class _Hook[T]:
    def __init__(self, callbacks: Any, *, after: bool) -> None:
        self.callbacks = callbacks
        self.after = after

    @overload
    def __call__(
        self: _Hook[AppCommandMeta],
        obj: Includable[AppCommandMeta],
    ) -> Includable[AppCommandMeta]: ...

    @overload
    def __call__[E: Event](
        self: _Hook[EventMeta[E]],
        obj: Includable[EventMeta[E]],
    ) -> Includable[EventMeta[E]]: ...

    def __call__(self, obj: Includable[AppCommandMeta | EventMeta[Event]]) -> Includable[Any]:
        obj.metadata.add_hooks(self.callbacks, prepend=True, after=self.after)

        return obj


def add_hooks(
    obj: Includable[AppCommandMeta | EventMeta[Event]],
    command_hooks: Sequence[CommandHookCallbackT],
    command_after_hooks: Sequence[CommandHookCallbackT],
    event_hooks: Sequence[EventHookCallbackT[Event]],
    event_after_hooks: Sequence[EventHookCallbackT[Event]],
) -> None:
    match obj.metadata:
        case AppCommandMeta():
            obj.metadata.add_hooks(command_hooks, after=False)
            obj.metadata.add_hooks(command_after_hooks, after=True)
        case EventMeta():
            obj.metadata.add_hooks(event_hooks, after=False)
            obj.metadata.add_hooks(event_after_hooks, after=True)
