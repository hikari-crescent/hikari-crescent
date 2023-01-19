from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol, Sequence, Generic, TypeVar
from typing_extensions import ParamSpec

if TYPE_CHECKING:
    from crescent.internal.includable import Includable
    from crescent.typedefs import HookCallbackT

__all__: Sequence[str] = ("HookResult", "hook", "add_hooks")


T = TypeVar("T", contravariant=True)
P = ParamSpec("P")


class Hookable(Protocol[T]):
    def add_hooks(self, hooks: Sequence[T], prepend: bool = False, *, after: bool) -> None:
        ...


@dataclass
class HookResult:
    exit: bool = False


class hook(Generic[T]):
    def __init__(self, *callbacks: T, after: bool = False):
        self.callbacks = callbacks
        self.after = after

    def __call__(self, command: Includable[Hookable[T]]) -> Includable[Hookable[T]]:
        command.metadata.add_hooks(self.callbacks, prepend=True, after=self.after)
        return command


class HasHooks(Protocol):
    hooks: list[HookCallbackT] | None
    after_hooks: list[HookCallbackT] | None


class HasHooksLongName(Protocol):
    command_hooks: list[HookCallbackT] | None
    command_after_hooks: list[HookCallbackT] | None


def add_hooks(obj: HasHooks | HasHooksLongName, command: Includable[Hookable[Any]]) -> None:
    command_hooks = getattr(obj, "hooks", None) or getattr(obj, "command_hooks", None)
    command_after_hooks = getattr(obj, "after_hooks", None) or getattr(
        obj, "command_after_hooks", None
    )

    if command_hooks:
        command.metadata.add_hooks(command_hooks, after=False)
    if command_after_hooks:
        command.metadata.add_hooks(command_after_hooks, after=True)
