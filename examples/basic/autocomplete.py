from __future__ import annotations

import hikari

import crescent

bot = hikari.GatewayBot(token="...")
client = crescent.Client(bot)


async def autocomplete_response(
    ctx: crescent.AutocompleteContext, option: hikari.AutocompleteInteractionOption
) -> list[tuple[str, str]]:
    # All the other options are stored in ctx.options
    # returns a list of tuples of (option name, option value).
    return [("Some Option", "1234")]


async def fetch_autocomplete_options(
    ctx: crescent.AutocompleteContext, option: hikari.AutocompleteInteractionOption
) -> list[tuple[str, str]]:
    # Return options with snowflakes converted into the option types.
    # This function can be extremely expensive.
    _options = await ctx.fetch_options()

    # Return no options.
    return []


@client.include
@crescent.command
class class_example:
    result = crescent.option(str, "Respond to the message", autocomplete=autocomplete_response)

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.respond(self.result, ephemeral=True)


bot.run()
