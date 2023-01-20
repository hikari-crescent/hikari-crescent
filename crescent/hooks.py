from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, Protocol, Sequence, TypeVar

if TYPE_CHECKING:
    from crescent.internal.includable import Includable

__all__: Sequence[str] = ("HookResult", "hook", "add_hooks")


T = TypeVar("T", contravariant=True)


class Hookable(Protocol[T]):
    def add_hooks(self, hooks: Sequence[T], prepend: bool = False, *, after: bool) -> None:
        ...


@dataclass
class HookResult:
    __slots__ = ("exit",)

    exit: bool = False


class hook(Generic[T]):
    def __init__(self, *callbacks: T, after: bool = False):
        self.callbacks = callbacks
        self.after = after

    def __call__(self, includable: Includable[Hookable[T]]) -> Includable[Hookable[T]]:
        includable.metadata.add_hooks(self.callbacks, prepend=True, after=self.after)
        return includable


def add_hooks(
    includable: Includable[Hookable[T]],
    *,
    hooks: Sequence[T] | None,
    after_hooks: Sequence[T] | None,
) -> None:
    if hooks:
        includable.metadata.add_hooks(hooks, after=False)
    if after_hooks:
        includable.metadata.add_hooks(after_hooks, after=True)
