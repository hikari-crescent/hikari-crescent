import crescent

plugin = crescent.Plugin()


@plugin.include
@crescent.command
async def nested_plugin(ctx: crescent.Context):
    await ctx.respond("Working!")
