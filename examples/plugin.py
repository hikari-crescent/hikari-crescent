import hikari

import crescent

plugin = crescent.Plugin("example")


@plugin.include
@crescent.command
async def plugin_command(ctx):
    await ctx.respond("plugins work")


@plugin.include
@crescent.event
async def plugin_event(event: hikari.MessageCreateEvent):
    print("plugin event triggered")
