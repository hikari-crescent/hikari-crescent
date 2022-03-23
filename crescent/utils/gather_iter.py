from asyncio import gather
from typing import Any, Iterable, Sequence

__all__: Sequence[str] = ("gather_iter",)


async def gather_iter(iterable: Iterable[Any]) -> Any:
    return await gather(*iterable)
