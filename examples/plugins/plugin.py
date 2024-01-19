import typing

import hikari

import crescent

if typing.TYPE_CHECKING:
    pass

# If you are not using the model property you can typehint as
# `crescent.Plugin[hikari.GatewayBot, None]` instead.
plugin = crescent.Plugin[hikari.GatewayBot, "Model"]()


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

    # The model attribute is accessible once the plugin is loaded.
    print(plugin.model)


@plugin.unload_hook
def on_unload() -> None:
    print("UNLOADED")
