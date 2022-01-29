from __future__ import annotations

from functools import partial
from inspect import iscoroutinefunction
from typing import TYPE_CHECKING, Sequence, overload

from attrs import define

from crescent.internal.meta_struct import MetaStruct

if TYPE_CHECKING:
    from typing import Any, Awaitable, Callable, Optional, TypeVar

    from crescent.typedefs import CommandOptionsT, HookCallbackT

    T = TypeVar("T", bound="MetaStruct[Callable[..., Awaitable[Any]], Any]")

__all__: Sequence[str] = (
    "HookResult",
    "hook",
)


@define
class HookResult:
    exit: bool = False
    options: Optional[CommandOptionsT] = None


@overload
def hook(callback: HookCallbackT, /) -> Callable[..., T]:
    ...


@overload
def hook(callback: HookCallbackT, command: T, /) -> T:
    ...


def hook(callback, command=None):

    if command is None:
        return partial(hook, callback)

    if not iscoroutinefunction(callback):
        raise ValueError(f"Function `{callback.__name__}` must be async.")

    command.interaction_hooks.insert(0, callback)

    return command
