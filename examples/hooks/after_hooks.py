import hikari
import crescent

# Hooks can be executed after commands.
# After hooks are NOT run when there is an exception.

bot = hikari.GatewayBot(token="...")
client = crescent.Client(bot)


async def hook(ctx: crescent.Context) -> None:
    print("Here after the command")


@client.include
@crescent.hook(hook, after=True)
@crescent.command
async def say(ctx: crescent.Context, word: str) -> None:
    await ctx.respond(word)

bot.run()
