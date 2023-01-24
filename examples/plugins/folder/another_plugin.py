import hikari

import crescent

plugin = crescent.Plugin[hikari.GatewayBot]()


@plugin.include
@crescent.command
async def nested_plugin(ctx: crescent.Context) -> None:
    await ctx.respond("Working!")
