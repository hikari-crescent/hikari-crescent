from typing import Any, Awaitable, Callable, Optional

from hikari import Snowflake
from pycooldown import FixedCooldown

from crescent import Context, HookResult

__all__ = ("CooldownCallbackT", "BucketCallbackT", "cooldown")

CooldownCallbackT = Callable[[Context, float], Awaitable[Optional[HookResult]]]
BucketCallbackT = Callable[[Context], Any]


def _default_bucket(ctx: Context) -> Snowflake:
    return ctx.user.id


def cooldown(
    period: float,
    capacity: int,
    *,
    callback: Optional[CooldownCallbackT] = None,
    bucket: Optional[BucketCallbackT] = _default_bucket,
) -> Callable[[Context], Awaitable[Optional[HookResult]]]:
    """
    Ratelimit implementation using a sliding window.

    Args:
        period:
            The period of time, in seconds, between cooldown resets.
        capacity:
            The amount of times the command can be used within the period.
        callback:
            Callback for when a user is ratelimited.
        bucket:
            Callback that returns a key for a bucket.
    """
    cooldown: FixedCooldown[Any] = FixedCooldown(period, capacity)

    async def inner(ctx: Context) -> Optional[HookResult]:
        retry_after = cooldown.update_ratelimit(bucket(ctx))

        if not retry_after:
            return None

        if callback:
            await callback(ctx, retry_after)
        else:
            # Default response for when there is no callback
            await ctx.respond(f"You are rate limited! Try again in {retry_after:.2f}s.")
        return HookResult(exit=True)

    return inner
