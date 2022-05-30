from __future__ import annotations

from functools import partial
from inspect import iscoroutinefunction
from typing import TYPE_CHECKING, get_type_hints, overload

from crescent.internal.meta_struct import MetaStruct
from crescent.utils.options import unwrap

if TYPE_CHECKING:
    from typing import Any, Callable, Coroutine, Optional, Sequence, Type

    from hikari import Event
    from hikari.api.event_manager import CallbackT


__all__: Sequence[str] = ("event",)


@overload
def event(callback: CallbackT[Any], /) -> MetaStruct[CallbackT[Any], None]:
    ...


@overload
def event(
    *, event_type: Optional[Type[Any]]
) -> Callable[[CallbackT[Any]], MetaStruct[CallbackT[Any], None]]:
    ...


def event(
    callback: CallbackT[Any] | None = None, /, *, event_type: Optional[Type[Any]] = None
) -> Callable[[CallbackT[Any]], MetaStruct[CallbackT[Any], None]] | MetaStruct[
    CallbackT[Any], None
]:
    if callback is None:
        return partial(event, event_type=event_type)

    if not event_type:
        event_type = next(iter(get_type_hints(callback).values()))

    if not event_type:
        raise ValueError("`event_type` must be provided in the decorator or as a typehint")

    if not iscoroutinefunction(callback):
        raise ValueError(f"`{callback.__name__}` must be an async function.")

    def hook(self: MetaStruct[CallbackT[Any], None]) -> None:
        self.app.subscribe(event_type=unwrap(event_type), callback=_event_callback(self))

    return MetaStruct(callback=callback, metadata=None, app_set_hooks=[hook])


def _event_callback(
    self: MetaStruct[CallbackT[Any], None]
) -> Callable[[Event], Coroutine[None, None, None]]:
    async def func(event: Event) -> None:
        try:
            await self.callback(event)
        except Exception as exc:
            handled = await self.app._event_error_handler.try_handle(exc, [exc, event])
            await self.app.on_crescent_event_error(exc, event, handled)

    return func
