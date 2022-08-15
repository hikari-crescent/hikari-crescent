from __future__ import annotations

from functools import partial
from inspect import iscoroutinefunction
from typing import TYPE_CHECKING, Sequence, overload, Any, Protocol

from attrs import define

from crescent.internal.app_command import AppCommandMeta
from crescent.internal.includable import Includable

if TYPE_CHECKING:
    from typing import Callable

    from crescent.internal.app_command import AppCommandMeta
    from crescent.internal.includable import Includable
    from crescent.typedefs import HookCallbackT

__all__: Sequence[str] = ("HookResult", "hook", "add_hooks")


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
    command.metadata.add_hooks([callback], prepend=True, after=after)

    return command

class HasHooksA(Protocol):
    command_hooks: list[HookCallbackT] | None
    command_after_hooks: list[HookCallbackT] | None

class HasHooksB(Protocol):
    hooks: list[HookCallbackT] | None
    after_hooks: list[HookCallbackT] | None


def add_hooks(obj: HasHooksA | HasHooksB, command: Includable[Any]) -> None:
    if not isinstance(command.metadata, AppCommandMeta):
        return

    command_hooks = getattr(obj, "hooks", None) or getattr(obj, "command_hooks", None)
    command_after_hooks = getattr(obj, "after_hooks", None) or getattr(obj, "command_after_hooks", None)

    if command_hooks:
        command.metadata.add_hooks(command_hooks, after=False)
    if command_after_hooks:
        command.metadata.add_hooks(command_after_hooks, after=True)
