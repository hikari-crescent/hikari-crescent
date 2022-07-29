from __future__ import annotations

from functools import partial
from inspect import iscoroutinefunction
from typing import TYPE_CHECKING, Sequence, overload

from attrs import define

if TYPE_CHECKING:
    from typing import Callable

    from crescent.internal.app_command import AppCommandMeta
    from crescent.internal.includable import Includable
    from crescent.typedefs import HookCallbackT

__all__: Sequence[str] = ("HookResult", "hook")


@define
class HookResult:
    exit: bool = False


@overload
def hook(
    callback: HookCallbackT, *, after: bool = False
) -> Callable[..., Includable[AppCommandMeta]]:
    ...


@overload
def hook(
    callback: HookCallbackT, *, command: Includable[AppCommandMeta]
) -> Includable[AppCommandMeta]:
    ...


def hook(
    callback: HookCallbackT, after: bool = False, command: Includable[AppCommandMeta] | None = None
) -> Includable[AppCommandMeta] | Callable[..., Includable[AppCommandMeta]]:
    if command is None:
        return partial(hook, callback, after)  # type: ignore
    if not iscoroutinefunction(callback):
        raise ValueError(f"Function `{callback.__name__}` must be async.")
    if after:
        command.metadata.after_hooks.insert(0, callback)
    else:
        command.metadata.hooks.insert(0, callback)

    return command
