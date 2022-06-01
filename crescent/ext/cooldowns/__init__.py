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

    period:
        The amount of time between each ratelimit.
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
            return HookResult(exit=True)
        else:
            return None

    return inner
