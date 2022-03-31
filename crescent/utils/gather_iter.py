from asyncio import gather
from typing import Sequence

__all__: Sequence[str] = ("gather_iter",)


async def gather_iter(iterable):
    return await gather(*iterable)
