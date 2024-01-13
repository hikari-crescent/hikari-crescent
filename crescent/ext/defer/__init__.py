from __future__ import annotations

from asyncio import sleep
from collections.abc import Awaitable
from datetime import timedelta
from typing import Callable, overload

from crescent import Context
from crescent.utils import create_task


async def defer(ctx: Context) -> None:
    await ctx.defer()


async def _noop():
    pass


@overload
def autodefer(ctx: Context) -> Awaitable[None]:
    ...


@overload
def autodefer(*, time: timedelta | None = None) -> Callable[[Context], Awaitable[None]]:
    ...


def autodefer(
    ctx: Context | None = None, *, time: timedelta | None = None
) -> Awaitable[None] | Callable[[Context], Awaitable[None]]:
    if not time and not ctx:
        return autodefer()

    async def task():
        assert ctx
        await sleep((time or timedelta(seconds=2)).total_seconds())
        if ctx._has_deferred_response or ctx._has_created_response:
            return
        else:
            await ctx.defer()

    create_task(task())

    return _noop()
