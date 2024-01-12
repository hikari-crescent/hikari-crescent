from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Sequence, TypeVar, Generic, overload, Any
from crescent.events import EventMeta

from crescent.internal.app_command import AppCommandMeta
from crescent.typedefs import EventHookCallbackT
from hikari import Event

if TYPE_CHECKING:
    from crescent.internal.includable import Includable
    from crescent.typedefs import HookCallbackT

T = TypeVar("T")
IncludableT = TypeVar("IncludableT")
EventT = TypeVar("EventT", bound=Event, covariant=True)

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
def hook(*callbacks: HookCallbackT, after: bool = False) -> _Hook[AppCommandMeta]:
    ...


@overload
def hook(*callbacks: EventHookCallbackT[EventT], after: bool = False) -> _Hook[EventMeta[EventT]]:
    ...


def hook(
    *callbacks: HookCallbackT | EventHookCallbackT[EventT], after: bool = False
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

    def __call__(self, obj: Includable[IncludableT]) -> Includable[IncludableT]:
        if isinstance(obj.metadata, AppCommandMeta):
            obj.metadata.add_hooks(self.callbacks, prepend=True, after=self.after)

        elif isinstance(obj.metadata, EventMeta):
            raise Exception

        else:
            raise TypeError("Unsupported type, this should never happen.")

        return obj

def add_hooks(
    hooks: list[T], after_hooks: list[T], hooks_to_add: Sequence[T], *, prepend: bool, after: bool
) -> None:
    def extend_or_prepend(list_to_edit: list[T]) -> None:
        if prepend:
            list_to_edit[:0] = hooks_to_add
        else:
            list_to_edit.extend(hooks_to_add)

    if not after:
        extend_or_prepend(hooks)
    else:
        extend_or_prepend(after_hooks)
