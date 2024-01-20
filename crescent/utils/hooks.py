from __future__ import annotations

from typing import Sequence, TypeVar

__all__: Sequence[str] = ("add_hooks",)

T = TypeVar("T")


def add_hooks(
    hooks: list[T], after_hooks: list[T], hooks_to_add: Sequence[T], *, prepend: bool, after: bool
) -> None:
    def extend_or_prepend(list_to_edit: list[T]) -> None:
        if prepend:
            list_to_edit[:0] = hooks_to_add
        else:
            list_to_edit.extend(hooks_to_add)

    if not after:
        extend_or_prepend(hooks)
    else:
        extend_or_prepend(after_hooks)
