from typing import Tuple

import hikari
import crescent
from crescent.ext import cooldowns

bot = crescent.Bot("...")


def guild_specific_rate_limits(ctx: crescent.Context) -> Tuple[hikari.Snowflake, hikari.Snowflake]:
    return (ctx.user.id, ctx.guild.id)

# This function now has individual rate limit buckets for each guild.
@bot.include
@crescent.hook(cooldowns.cooldown(20, 3, bucket=guild_specific_rate_limits))
@crescent.command
async def my_command(ctx: crescent.Context) -> None:
    await ctx.respond("Hello!")


bot.run()
