import crescent

bot = crescent.Bot("...")


class RandomError(Exception):
    pass


class RandomError2(Exception):
    pass


class RandomError3(Exception):
    pass


@bot.include
@crescent.catch(RandomError)
async def on_random_error(exc: RandomError, ctx: crescent.Context) -> None:
    await ctx.respond(f"{exc} raised in {ctx.command}!")


@bot.include
@crescent.catch(RandomError2, RandomError3)
async def on_random_error_2(exc: Exception, ctx: crescent.Context) -> None:
    await ctx.respond(f"{exc} raised in {ctx.command}!")


@bot.include
@crescent.command
async def raise_error(ctx: crescent.Context):
    raise RandomError("Lol")


bot.run()
