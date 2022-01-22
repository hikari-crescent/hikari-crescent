from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, get_type_hints

from hikari import GatewayBot

if TYPE_CHECKING:
    from typing import Any, Callable, Sequence, Type
    from hikari.api.event_manager import CallbackT, EventT_co


def event(
    callback: CallbackT[Any] = None,
    event_type: Type[Any] = None
):
    if callback is None:
        return partial(event, event_type=event_type)

    if not event_type:
        event_type = next(iter(get_type_hints(callback).values()))

    if not event_type:
        raise ValueError(
            "`event_type` must be provided in the decorator or as a typehint"
        )

    return Partial(GatewayBot.subscribe, event_type, callback)


class Partial:

    __slots__: Sequence[str] = (
        "owner",
        "call",
        "args",
        "kwargs"
    )

    def __init__(self, call: Callable[..., Any], *args, **kwargs) -> None:
        self.call = call
        self.args = args
        self.kwargs = kwargs

    def __call__(self, owner):
        self.call(owner, *self.args, **self.kwargs)
