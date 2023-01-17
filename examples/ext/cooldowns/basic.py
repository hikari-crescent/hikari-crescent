import hikari

import crescent
from crescent.ext import cooldowns

bot = hikari.GatewayBot(token="...")
client = crescent.Client(bot)


# The user can use the command 3 times in 20 seconds.
@client.include
@crescent.hook(cooldowns.cooldown(3, 20))
@crescent.command
async def my_command(ctx: crescent.Context) -> None:
    await ctx.respond("Hello!")


# Callbacks can be set to run when a user is ratelimited.
async def on_rate_limited(ctx: crescent.Context, time_remaining: float) -> None:
    await ctx.respond(f"You are ratelimited for {time_remaining}s.")


@client.include
@crescent.hook(cooldowns.cooldown(1, 100, callback=on_rate_limited))
@crescent.command
async def my_command2(ctx: crescent.Context) -> None:
    await ctx.respond("Hello!")


bot.run()
