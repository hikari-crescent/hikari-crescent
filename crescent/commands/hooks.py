from __future__ import annotations

from dataclasses import dataclass
from inspect import iscoroutinefunction
from typing import TYPE_CHECKING, Any, Protocol, Sequence

from crescent.internal.app_command import AppCommandMeta

if TYPE_CHECKING:
    from crescent.internal.includable import Includable
    from crescent.typedefs import HookCallbackT

__all__: Sequence[str] = ("HookResult", "hook", "add_hooks")


@dataclass
class HookResult:
    exit: bool = False


class hook:
    def __init__(self, *callbacks: HookCallbackT, after: bool = False):
        self.callbacks = callbacks
        self.after = after

    def __call__(self, command: Includable[AppCommandMeta]) -> Includable[AppCommandMeta]:
        for callback in self.callbacks:
            if not iscoroutinefunction(callback):
                raise ValueError(f"Function `{callback.__name__}` must be async.")
        command.metadata.add_hooks(self.callbacks, prepend=True, after=self.after)

        return command


class HasHooks(Protocol):
    hooks: list[HookCallbackT] | None
    after_hooks: list[HookCallbackT] | None


class HasHooksLongName(Protocol):
    command_hooks: list[HookCallbackT] | None
    command_after_hooks: list[HookCallbackT] | None


def add_hooks(obj: HasHooks | HasHooksLongName, command: Includable[Any]) -> None:
    if not isinstance(command.metadata, AppCommandMeta):
        return

    command_hooks = getattr(obj, "hooks", None) or getattr(obj, "command_hooks", None)
    command_after_hooks = getattr(obj, "after_hooks", None) or getattr(
        obj, "command_after_hooks", None
    )

    if command_hooks:
        command.metadata.add_hooks(command_hooks, after=False)
    if command_after_hooks:
        command.metadata.add_hooks(command_after_hooks, after=True)
