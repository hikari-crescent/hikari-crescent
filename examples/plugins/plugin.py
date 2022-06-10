import hikari

import crescent

plugin = crescent.Plugin()


@plugin.include
@crescent.command
async def plugin_command(ctx):
    await ctx.respond("plugins work")


@plugin.include
@crescent.event
async def plugin_event(event: hikari.MessageCreateEvent):
    print("plugin event triggered")


# You can run functions when a plugin is loaded and unloaded


@plugin.load_hook
def on_load():
    print("LOADED")


# Unload is automatically called when the bot is closed (hikari.StoppedEvent)
@plugin.unload_hook
def on_unload():
    print("UNLOADED")
