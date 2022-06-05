import crescent

# Hooks can be executed after commands

bot = crescent.Bot("...")


async def hook(ctx: crescent.Context) -> None:
    print("Here after the command")


@bot.include
@crescent.hook(hook, after=True)
@crescent.command
async def say(ctx: crescent.Context, word: str):
    await ctx.respond(word)
