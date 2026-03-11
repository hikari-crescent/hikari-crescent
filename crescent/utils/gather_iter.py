from __future__ import annotations

from asyncio import gather
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from collections.abc import Awaitable, Iterable

__all__ = ("gather_iter",)


T = TypeVar("T")


async def gather_iter(iterable: Iterable[Awaitable[T]]) -> Iterable[T]:
    return await gather(*iterable)
