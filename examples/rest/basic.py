import asyncio

from hikari import RESTBot, TokenType

from crescent import Client, command, Context


bot = RESTBot("...", TokenType.BOT)
client = Client(bot)


@client.include
@command(name="ping", description="Pong!")
async def ping(ctx: Context) -> None:
    await ctx.defer()
    await asyncio.sleep(2)
    await ctx.respond("heyo")


bot.run()
