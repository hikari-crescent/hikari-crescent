from __future__ import annotations

from datetime import timedelta
from typing import Any, Awaitable, Callable, Optional

from hikari import Snowflake

from crescent import Context, HookResult

__all__ = ("CooldownCallbackT", "BucketCallbackT", "cooldown")

CooldownCallbackT = Callable[[Context, timedelta], Awaitable[Optional[HookResult]]]
BucketCallbackT = Callable[[Context], Any]


def _default_bucket(ctx: Context) -> Snowflake:
    return ctx.user.id


async def _default_callback(ctx: Context, retry: timedelta) -> None:
    seconds = round(retry.total_seconds())
    if seconds <= 1:
        message = "1 second"
    else:
        message = f"{seconds} seconds"
    await ctx.respond(
        f"You're using this command too much! Try again in {message}.", ephemeral=True
    )


def cooldown(
    capacity: int,
    period: timedelta,
    *,
    callback: CooldownCallbackT = _default_callback,
    bucket: BucketCallbackT = _default_bucket,
) -> Callable[[Context], Awaitable[HookResult | None]]:
    """
    Ratelimit implementation using a sliding window.

    Args:
        capacity:
            The amount of times the command can be used within the period.
        period:
            The period of time, in seconds, between cooldown resets.
        callback:
            Callback for when a user is ratelimited.
        bucket:
            Callback that returns a key for a bucket.
    """

    try:
        from floodgate import FixedMapping
    except ImportError:
        raise ModuleNotFoundError(
            "`hikari-crescent[cooldowns]` must be installed to use `crescent.ext.cooldowns`."
        )

    cooldown: FixedMapping[Any] = FixedMapping(period=period, capacity=capacity)

    async def inner(ctx: Context) -> HookResult | None:
        retry_after = cooldown.trigger(bucket(ctx))

        if not retry_after:
            return None

        await callback(ctx, retry_after)
        return HookResult(exit=True)

    return inner
