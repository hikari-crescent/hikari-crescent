from typing import Awaitable, Callable
from crescent import HookResult, Context
from pycooldown import FixedCooldown

CooldownCallbackT = Callable[[Context], Awaitable[None]]


def cooldown(period: float, capacity: int, callback: CooldownCallbackT):
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
        retry_after = cooldown.update_ratelimit(ctx.user.id)

        if retry_after:
            await callback(ctx)
            return HookResult(exit=True)
        else:
            return None

    return inner
