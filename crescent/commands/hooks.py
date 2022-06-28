from __future__ import annotations

from functools import partial
from inspect import iscoroutinefunction
from typing import TYPE_CHECKING, Sequence, overload

from attrs import define

if TYPE_CHECKING:
    from typing import Any, Awaitable, Callable, TypeVar

    from crescent.internal.app_command import AppCommandMeta
    from crescent.internal.meta_struct import MetaStruct
    from crescent.typedefs import HookCallbackT

    T = TypeVar("T", bound="MetaStruct[Callable[..., Awaitable[Any]], AppCommandMeta]")

__all__: Sequence[str] = ("HookResult", "hook")


@define
class HookResult:
    exit: bool = False


@overload
def hook(
    callback: HookCallbackT, *, after: bool = False
) -> Callable[..., MetaStruct[Callable[..., Awaitable[Any]], AppCommandMeta]]:
    ...


@overload
def hook(callback: HookCallbackT, *, command: T) -> T:
    ...


def hook(
    callback: HookCallbackT, after: bool = False, command: T | None = None
) -> T | Callable[..., T]:
    if command is None:
        return partial(hook, callback, after)  # type: ignore
    if not iscoroutinefunction(callback):
        raise ValueError(f"Function `{callback.__name__}` must be async.")
    if after:
        command.metadata.after_hooks.insert(0, callback)
    else:
        command.metadata.hooks.insert(0, callback)

    return command
