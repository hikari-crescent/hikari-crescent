from __future__ import annotations

from dataclasses import dataclass, field
from functools import partial
from inspect import iscoroutinefunction
from typing import TYPE_CHECKING, Generic, TypeVar, get_type_hints, overload

from hikari import EventManagerAware

from crescent.internal.includable import Includable
from crescent.typedefs import EventHookCallbackT
from crescent.utils import add_hooks
from crescent.utils.options import unwrap

if TYPE_CHECKING:
    from typing import Any, Callable, Coroutine, Sequence

    from hikari import Event
    from hikari.api.event_manager import CallbackT

EventT = TypeVar("EventT", bound="Event", contravariant=True)

__all__: Sequence[str] = ("event",)


@dataclass
class EventMeta(Generic[EventT]):
    callback: CallbackT[EventT]
    hooks: list[EventHookCallbackT[EventT]] = field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]
    after_hooks: list[EventHookCallbackT[EventT]] = field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]

    def add_hooks(
        self, hooks: Sequence[EventHookCallbackT[Any]], prepend: bool = False, *, after: bool
    ) -> None:
        add_hooks(self.hooks, self.after_hooks, hooks, prepend=prepend, after=after)


@overload
def event(callback: CallbackT[EventT], /) -> Includable[EventMeta[EventT]]: ...


@overload
def event(
    *, event_type: type[EventT] | None
) -> Callable[[CallbackT[EventT]], Includable[EventMeta[EventT]]]: ...


def event(
    callback: CallbackT[EventT] | None = None, /, *, event_type: type[EventT] | None = None
) -> Callable[[CallbackT[EventT]], Includable[EventMeta[EventT]]] | Includable[EventMeta[EventT]]:
    """
    Listen to an event. This function should be used instead of
    `hikari.GatewayBot.listen` whenever possible.

    ### Example
    ```python
    import crescent

    client = crescent.Client(...)

    # Listen to the message create event
    @client.include
    @crescent.event
    async def ping(event: hikari.MessageCreateEvent):
        ...
    ```

    Event types can be provided using the `event_type` kwarg if you do not want
    to use type annotations.
    """
    if callback is None:
        return partial(event, event_type=event_type)  # pyright: ignore

    if not event_type:
        event_type = next(iter(get_type_hints(callback).values()))

    if not event_type:
        raise ValueError("`event_type` must be provided in the decorator or as a typehint")

    if not iscoroutinefunction(callback):
        raise ValueError(f"`{callback.__name__}` must be an async function.")

    def hook(includable: Includable[EventMeta[EventT]]) -> None:
        if isinstance(includable.client.app, EventManagerAware):
            includable.client.app.event_manager.subscribe(
                event_type=unwrap(event_type), callback=event_callback
            )
        else:
            raise ValueError(
                "Events can only be used with bots that implement `hikari.EventManagerAware`."
            )

    def on_remove(includable: Includable[EventMeta[EventT]]) -> None:
        # if it's not `EventManagerAware`, the event could never have been
        # added in the first place.
        assert isinstance(includable.client.app, EventManagerAware)
        includable.client.app.event_manager.unsubscribe(
            event_type=unwrap(event_type), callback=event_callback
        )

    includable = Includable(
        metadata=EventMeta(callback=callback),
        client_set_hooks=[hook],
        plugin_unload_hooks=[on_remove],
    )
    event_callback = _event_callback(includable)

    return includable


def _event_callback(
    self: Includable[EventMeta[Any]],
) -> Callable[[Event], Coroutine[None, None, None]]:
    async def func(event: Event) -> None:
        try:
            for callback in self.metadata.hooks:
                res = await callback(event)
                if res and res.exit is True:
                    return
            await self.metadata.callback(event)
            for callback in self.metadata.after_hooks:
                res = await callback(event)
                if res and res.exit is True:
                    return
        except Exception as exc:
            handled = await self.client._event_error_handler.try_handle(exc, [exc, event])
            await self.client.on_crescent_event_error(exc, event, handled)

    return func
