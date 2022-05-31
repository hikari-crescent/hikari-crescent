from typing import Awaitable, Callable, Optional

from pycooldown import FixedCooldown

from crescent import Context, HookResult

CooldownCallbackT = Callable[[Context, float], Awaitable[Optional[HookResult]]]


def cooldown(period: float, capacity: int, callback: Optional[CooldownCallbackT] = None):
    """
    period:
        The amount of of seconds for the ratelimit
    capacity:
        i have no idea
    callback:
        callback for when a user is ratelimited
    """
    cooldown = FixedCooldown(period, capacity)

    async def inner(ctx: Context):
        retry_after = cooldown.update_rate_limit(ctx.user.id)
        if retry_after:
            if callback:
                await callback(ctx, retry_after)
            return HookResult(exit=True)
        else:
            return None

    return inner
