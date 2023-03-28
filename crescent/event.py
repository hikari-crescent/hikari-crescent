from __future__ import annotations

from functools import partial
from inspect import iscoroutinefunction
from typing import TYPE_CHECKING, get_type_hints, overload

from crescent.client import GatewayTraits
from crescent.internal.includable import Includable
from crescent.utils.options import unwrap

if TYPE_CHECKING:
    from typing import Any, Callable, Coroutine, Sequence

    from hikari import Event
    from hikari.api.event_manager import CallbackT

__all__: Sequence[str] = ("event",)


@overload
def event(callback: CallbackT[Any], /) -> Includable[CallbackT[Any]]:
    ...


@overload
def event(
    *, event_type: type[Any] | None
) -> Callable[[CallbackT[Any]], Includable[CallbackT[Any]]]:
    ...


def event(
    callback: CallbackT[Any] | None = None, /, *, event_type: type[Any] | None = None
) -> Callable[[CallbackT[Any]], Includable[CallbackT[Any]]] | Includable[CallbackT[Any]]:
    if callback is None:
        return partial(event, event_type=event_type)

    if not event_type:
        event_type = next(iter(get_type_hints(callback).values()))

    if not event_type:
        raise ValueError("`event_type` must be provided in the decorator or as a typehint")

    if not iscoroutinefunction(callback):
        raise ValueError(f"`{callback.__name__}` must be an async function.")

    def hook(includable: Includable[CallbackT[Any]]) -> None:
        if isinstance(includable.client.app, GatewayTraits):
            includable.client.app.event_manager.subscribe(
                event_type=unwrap(event_type), callback=event_callback
            )
        else:
            raise ValueError("Events can only be used with GatewayBot.")

    def on_remove(includable: Includable[CallbackT[Any]]) -> None:
        # if it's not `GatewayTraits`, the event could never have been
        # added in the first place.
        assert isinstance(includable.client.app, GatewayTraits)
        includable.client.app.event_manager.unsubscribe(
            event_type=unwrap(event_type), callback=event_callback
        )

    includable = Includable(
        metadata=callback, client_set_hooks=[hook], plugin_unload_hooks=[on_remove]
    )
    event_callback = _event_callback(includable)

    return includable


def _event_callback(
    self: Includable[CallbackT[Any]],
) -> Callable[[Event], Coroutine[None, None, None]]:
    async def func(event: Event) -> None:
        try:
            await self.metadata(event)
        except Exception as exc:
            handled = await self.client._event_error_handler.try_handle(exc, [exc, event])
            await self.client.on_crescent_event_error(exc, event, handled)

    return func
