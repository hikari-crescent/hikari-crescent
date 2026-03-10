import hikari

import crescent
from crescent import options

# Hooks can be executed after commands.
# After hooks are NOT run when there is an exception.

bot = hikari.GatewayBot(token="...")
client = crescent.Client(bot)


async def hook(ctx: crescent.Context) -> None:
    print("Here after the command")


@client.include
@crescent.hook(hook, after=True)
@crescent.command(name="say")
class Say:
    word = options.string("The word to say")

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.respond(self.word)


bot.run()
