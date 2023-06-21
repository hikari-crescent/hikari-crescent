from __future__ import annotations

import hikari
from typing_extensions import Annotated as Atd

import crescent

bot = hikari.GatewayBot(token="...")
client = crescent.Client(bot)


class RandomError(Exception):
    pass


class UnhandledError(Exception):
    pass


# error handling
@client.include
@crescent.catch_command(RandomError)
async def on_cmd_random_error(exc: RandomError, ctx: crescent.Context) -> None:
    await ctx.respond(f"{exc} raised in {ctx.command}!")


@client.include
@crescent.catch_event(RandomError)
async def on_event_random_error(exc: RandomError, event: hikari.Event) -> None:
    print(f"{exc} raised in {event}!")


@client.include
@crescent.catch_autocomplete(RandomError)
async def on_autocomplete_random_error(
    exc: RandomError,
    ctx: crescent.AutocompleteContext,
    inter: hikari.AutocompleteInteractionOption,
) -> None:
    print(f"{exc} raised in autocomplete for {ctx.command}!")


# buggy command/event/autocompletes
@client.include
@crescent.command
async def raise_error_cmd(ctx: crescent.Context, unhandled: bool) -> None:
    if unhandled:
        raise UnhandledError("Unhandled error!")
    raise RandomError("Handled error")


@client.include
@crescent.event
async def raise_error_event(event: hikari.MessageCreateEvent) -> None:
    if event.author.is_bot:
        return
    if event.message.content is None:
        return

    if event.message.content == "!unhandled":
        raise UnhandledError("Unhandled error!")
    elif event.message.content == "!error":
        raise RandomError("Handled error")
    elif event.message.content.startswith("!"):
        await event.message.respond("Use !unhandled or !error")


async def autocomplete(
    ctx: crescent.AutocompleteContext, option: hikari.AutocompleteInteractionOption
) -> list[tuple[str, str]]:
    assert isinstance(option.value, str)
    if option.value == "unhandled":
        raise UnhandledError("Unhandled error!")
    elif option.value == "error":
        raise RandomError("Handled error")

    # returns a list of tuples of (option name, option value).
    return [("error", "error"), ("unhandled", "unhandled")]


@client.include
@crescent.command
async def autocomplete_error(
    ctx: crescent.Context,
    option: Atd[str, "Type error to error out", crescent.Autocomplete(autocomplete)],
) -> None:
    await ctx.respond(f"{option} (type unhandled or error inside option)")


bot.run()
