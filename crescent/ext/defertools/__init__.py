from __future__ import annotations

from asyncio import sleep
from collections.abc import Awaitable
from datetime import timedelta
from typing import Callable, overload

from crescent import Context
from crescent.utils import create_task

__all__ = ["defer", "autodefer"]


async def defer(ctx: Context) -> None:
    """
    Hook used to defer a task.

    ```python
    from crescent.ext.defer import defer

    async def lengthy_hook_that_takes_a_lot_time(ctx: crescent.Context):
        # Simulate something that takes a lot of time...
        await asyncio.sleep(5)

    @client.include
    @crescent.hook(defer, lengthy_hook_that_takes_a_lot_time)
    @crescent.command
    async def command(ctx: crescent.Context) -> None:
        await ctx.respond("Hello world!!")
    ```
    """
    await ctx.defer()


async def _noop() -> None:
    pass


@overload
def autodefer(*, time: timedelta | None = None) -> Callable[[Context], Awaitable[None]]:
    ...


@overload
def autodefer(ctx: Context, *, time: timedelta | None = None) -> Awaitable[None]:
    ...


def autodefer(
    ctx: Context | None = None, *, time: timedelta | None = None
) -> Awaitable[None] | Callable[[Context], Awaitable[None]]:
    """
    Hook used to defer tasks automatically, by default after two seconds.

    ```python
    from crescent.ext.defer import autodefer

    @client.include
    @crescent.hook(autodefer)
    @crescent.command
    async def command(ctx: crescent.Context) -> None:
        # Simulate a long task...
        await asyncio.sleep(10)

        await ctx.respond("Hello world!!")
    ```

    You can use this command hook globally for autodefer on your entire bot.

    ```python
    import hikari
    import crescent
    from crescent.ext.defer import autodefer

    bot = hikari.GatewayBot(...)
    client = crescent.Client(bot, command_hooks=[autodefer])
    ```

    Args:
        time:
            The time to wait before automatically deferring the task. By default
            this is two seconds.
    """
    if not ctx:

        async def partial(ctx: Context) -> None:
            return await autodefer(ctx, time=time)

        return partial

    # bool(timedelta()) is False
    if time is None:
        time = timedelta(seconds=2)

    async def task() -> None:
        assert ctx
        assert time is not None
        await sleep(time.total_seconds())
        if ctx._has_deferred_response or ctx._has_created_response:
            return
        else:
            await ctx.defer()

    create_task(task())

    return _noop()
