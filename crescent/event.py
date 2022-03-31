from __future__ import annotations

from functools import partial
from inspect import iscoroutinefunction
from typing import TYPE_CHECKING, Callable, get_type_hints, overload

from crescent.internal.meta_struct import MetaStruct
from crescent.utils.options import unwrap

if TYPE_CHECKING:
    from typing import Any, Optional, Sequence, Type

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
        self.app.subscribe(event_type=unwrap(event_type), callback=self.callback)

    return MetaStruct(callback=callback, metadata=None, app_set_hooks=[hook])
