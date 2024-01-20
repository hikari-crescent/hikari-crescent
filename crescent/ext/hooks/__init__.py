from __future__ import annotations

from collections.abc import Awaitable
from typing import Callable, Protocol, overload, Sequence

from hikari import MessageCreateEvent

from crescent import Context
from crescent.hooks import HookResult

__all__: Sequence[str] = ("defer", "is_human")


@overload
def defer(*, ephemeral: bool = ...) -> Callable[[Context], Awaitable[None]]:
    pass


@overload
def defer(ctx: Context) -> Awaitable[None]:
    pass


def defer(
    ctx: Context | None = None, *, ephemeral: bool = False
) -> Callable[[Context], Awaitable[None]] | Awaitable[None]:
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
    if ctx is not None:
        return ctx.defer(ephemeral=ephemeral)

    return lambda ctx: ctx.defer(ephemeral=ephemeral)


async def is_human(event: MessageCreateEvent) -> HookResult:
    if event.is_human:
        return HookResult()
    return HookResult(exit=True)


async def is_bot(event: MessageCreateEvent) -> HookResult:
    if event.is_bot:
        return HookResult()
    return HookResult(exit=True)
