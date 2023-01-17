from __future__ import annotations

import hikari

import crescent
from crescent.ext import cooldowns

bot = hikari.GatewayBot(token="...")
client = crescent.Client(bot)


def guild_specific_rate_limits(
    ctx: crescent.Context,
) -> tuple[hikari.Snowflake, hikari.Snowflake | None]:
    return (ctx.user.id, ctx.guild_id)


# This function now has individual rate limit buckets for each guild.
@client.include
@crescent.hook(cooldowns.cooldown(3, 20, bucket=guild_specific_rate_limits))
@crescent.command
async def my_command(ctx: crescent.Context) -> None:
    await ctx.respond("Hello!")


bot.run()
