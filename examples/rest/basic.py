from __future__ import annotations

import asyncio
import random

from hikari import AutocompleteInteractionOption, RESTBot, TokenType

import crescent

bot = RESTBot("...", TokenType.BOT)
client = crescent.Client(bot)


async def autocomplete_callback(
    ctx: crescent.AutocompleteContext, option: AutocompleteInteractionOption
) -> list[tuple[str, str]]:
    chars = [c for c in str(option.value)]
    random.shuffle(chars)
    shuffled = "".join(chars)
    value = f"Showing results for '{shuffled}'."
    return [(value, shuffled)]


@client.include
@crescent.command(name="ping", description="Pong!")
async def ping(ctx: crescent.Context) -> None:
    await ctx.defer()
    await asyncio.sleep(2)
    await ctx.respond("heyo")


@client.include
@crescent.command(name="autcomplete", description="Autocomplete Test")
class AutocompleteTest:
    option = crescent.option(str, "An option", autocomplete=autocomplete_callback)

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.respond(f"You said {self.option}!")


bot.run()
