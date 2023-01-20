from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, Literal, Protocol, Sequence, TypeVar, overload

if TYPE_CHECKING:
    from crescent.internal.app_command import AppCommandMeta
    from crescent.internal.includable import Includable

__all__: Sequence[str] = ("HookResult", "hook", "add_hooks")


T = TypeVar("T", contravariant=True)
U = TypeVar("U", contravariant=True)


class Hookable(Protocol[T, U]):
    @overload
    def add_hooks(
        self, hooks: Sequence[T], prepend: bool = False, *, after: Literal[False]
    ) -> None:
        ...

    @overload
    def add_hooks(
        self, hooks: Sequence[U], prepend: bool = False, *, after: Literal[True]
    ) -> None:
        ...

    def add_hooks(self, hooks: Sequence[T | U], prepend: bool = False, *, after: bool) -> None:
        ...


@dataclass
class HookResult:
    exit: bool = False


class hook(Generic[T, U]):
    def __init__(self, *callbacks: T, after: bool = False):
        self.callbacks = callbacks
        self.after = after

    # Due to typing limitations, overloads are used to make this __call__ more accurate
    # for crescent's built in types.
    @overload
    def __call__(self, includable: Includable[AppCommandMeta]) -> Includable[AppCommandMeta]:
        ...

    @overload
    def __call__(self, includable: Includable[Hookable[T, U]]) -> Includable[Hookable[T, U]]:
        ...

    def __call__(self, includable: Includable[Any]) -> Includable[Any]:
        includable.metadata.add_hooks(self.callbacks, prepend=True, after=self.after)
        return includable


def add_hooks(
    includable: Includable[Hookable[T, U]],
    *,
    hooks: Sequence[T] | None,
    after_hooks: Sequence[U] | None,
) -> None:
    if hooks:
        includable.metadata.add_hooks(hooks, after=False)
    if after_hooks:
        includable.metadata.add_hooks(after_hooks, after=True)
