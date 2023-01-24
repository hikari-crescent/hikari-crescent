import hikari

import crescent

plugin = crescent.Plugin[hikari.GatewayBot]()


@plugin.include
@crescent.command
async def plugin_command(ctx: crescent.Context) -> None:
    await ctx.respond("plugins work")


@plugin.include
@crescent.event
async def plugin_event(event: hikari.MessageCreateEvent) -> None:
    print("plugin event triggered")


# You can run functions when a plugin is loaded and unloaded


@plugin.load_hook
def on_load() -> None:
    print("LOADED")


# Unload hooks are automatically called when the bot is shut down (hikari.StoppedEvent)
@plugin.unload_hook
def on_unload() -> None:
    print("UNLOADED")
