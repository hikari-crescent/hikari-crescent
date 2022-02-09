import crescent

plugin = crescent.Plugin("plugin")


@plugin.include
@crescent.command
async def plugin_cmd(ctx: crescent.Context) -> None:
    await ctx.respond("plugins work")
