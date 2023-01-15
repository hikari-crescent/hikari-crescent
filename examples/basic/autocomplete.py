from typing import Sequence

import hikari
import typing_extensions

import crescent

bot = crescent.Bot(token="...")


async def autocomplete_response(
    ctx: crescent.AutocompleteContext, option: hikari.AutocompleteInteractionOption
) -> Sequence[hikari.CommandChoice]:
    # All the other options are stored in ctx.options
    return [hikari.CommandChoice(name="Some Option", value="1234")]


async def fetch_autocomplete_options(
    ctx: crescent.AutocompleteContext, option: hikari.AutocompleteInteractionOption
) -> Sequence[hikari.CommandChoice]:

    # Return options with snowflakes converted into the option types.
    # This function can be extremely expensive.
    _options = await ctx.fetch_options()

    # Return no options.
    return []


# Both these commands function identically
@bot.include
@crescent.command
async def functional_example(
    ctx: crescent.Context,
    result: typing_extensions.Annotated[str, crescent.Autocomplete(autocomplete_response)],
) -> None:
    await ctx.respond(result, ephemeral=True)


@bot.include
@crescent.command
class class_example:
    result = crescent.option(str, "Respond to the message", autocomplete=autocomplete_response)

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.respond(self.result, ephemeral=True)


bot.run()
