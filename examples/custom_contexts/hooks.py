import hikari

import crescent

bot = hikari.GatewayBot(token="...")
client = crescent.Client(bot)


class CustomContext(crescent.Context):
    def custom_method(self) -> str:
        return "hello"


# `ctx`` can be annotated with any subclass of `cresent.BaseContext` and that will be used
# as the context type.
async def my_hook(ctx: CustomContext) -> None:
    await ctx.respond(ctx.custom_method())


# Hooks with custom context can be added like normal.
@client.include
@crescent.hook(my_hook)
@crescent.command
async def command(ctx: crescent.Context) -> None:
    await ctx.respond("Here")


bot.run()
