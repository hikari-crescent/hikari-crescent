import crescent


async def plugin_hook(ctx: crescent.Context) -> None:
    await ctx.respond("Plugin wide hook called.")


async def command_hook(ctx: crescent.Context) -> None:
    await ctx.respond("Command hook called.")


plugin = crescent.Plugin("plugin", [plugin_hook])


@plugin.include
@crescent.hook(command_hook)
@crescent.command
async def plugin_cmd(ctx: crescent.Context) -> None:
    await ctx.respond("plugins work")


@plugin.load_hook
def on_load() -> None:
    print("Plugin loaded")


@plugin.unload_hook
def on_unload() -> None:
    print("Plugin unloaded")
