from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, get_type_hints

from crescent.internal.meta_struct import MetaStruct
from crescent.utils.options import unwrap

if TYPE_CHECKING:
    from typing import Any, Sequence, Type, Optional
    from hikari.api.event_manager import CallbackT


__all__: Sequence[str] = (
    "event",
)


def event(
    callback: Optional[CallbackT] = None,
    event_type: Optional[Type[Any]] = None
):
    if callback is None:
        return partial(event, event_type=event_type)

    if not event_type:
        event_type = next(iter(get_type_hints(callback).values()))

    if not event_type:
        raise ValueError(
            "`event_type` must be provided in the decorator or as a typehint"
        )

    def hook(self: MetaStruct[CallbackT, None]):
        if self.is_method:
            self.callback = partial(self.callback, self.manager)

        self.app.subscribe(
            event_type=unwrap(event_type),
            callback=self.callback,
        )

    return MetaStruct(
        callback=callback,
        metadata=None,
        app_set_hooks=[hook]
    )
