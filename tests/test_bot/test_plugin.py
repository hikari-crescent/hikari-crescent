import crescent


async def plugin_hook(ctx: crescent.Context) -> None:
    await ctx.respond(f"Plugin wide hook called.")


plugin = crescent.Plugin("plugin", [plugin_hook])


@plugin.include
@crescent.command
async def plugin_cmd(ctx: crescent.Context) -> None:
    await ctx.respond("plugins work")
