import crescent

plugin = crescent.Plugin("another one?")


@plugin.include
@crescent.command
async def nested_plugin(ctx: crescent.Context):
    await ctx.respond("yup.")
