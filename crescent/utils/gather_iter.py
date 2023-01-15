from asyncio import gather
from typing import Awaitable, Iterable, Sequence, TypeVar

__all__: Sequence[str] = ("gather_iter",)


T = TypeVar("T")


async def gather_iter(iterable: Iterable[Awaitable[T]]) -> Iterable[T]:
    return await gather(*iterable)
