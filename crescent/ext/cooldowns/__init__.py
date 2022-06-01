from typing import Awaitable, Callable, Optional

from hikari import Snowflakeish
from pycooldown import FixedCooldown

from crescent import Context, HookResult

CooldownCallbackT = Callable[[Context, float], Awaitable[Optional[HookResult]]]


def cooldown(
    period: float, capacity: int, callback: Optional[CooldownCallbackT] = None
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
    """
    cooldown: FixedCooldown[Snowflakeish] = FixedCooldown(period, capacity)

    async def inner(ctx: Context) -> Optional[HookResult]:
        retry_after = cooldown.update_ratelimit(ctx.user.id)
        if retry_after:
            if callback:
                await callback(ctx, retry_after)
            else:
                # Default response for when there is no callback
                await ctx.respond(f"You are rate limited! Try again in {retry_after:.2f}s.")
            return HookResult(exit=True)
        else:
            return None

    return inner
