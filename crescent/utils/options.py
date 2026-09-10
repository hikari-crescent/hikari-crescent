from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar, overload

if TYPE_CHECKING:
    from collections.abc import Callable

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")

__all__ = ("map_or", "unwrap")


def unwrap(o: T | None) -> T:
    if o is None:
        raise ValueError("Object is not defined")
    return o


@overload
def map_or(o: T | None, func: Callable[[T], U]) -> U | None: ...


@overload
def map_or(o: T | None, func: Callable[[T], U], default: V) -> U | V: ...


def map_or(o: T | None, func: Callable[[T], U], default: V | None = None) -> U | V | None:
    if o is None:
        return default
    return func(o)
