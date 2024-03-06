import asyncio
import os
from datetime import datetime
from typing import Sequence

import dotenv
import hikari

import crescent
from crescent.exceptions import ConverterException
from crescent.ext import tasks

dotenv.load_dotenv()


async def myhook(ctx: crescent.Context) -> None:
    await ctx.respond("Hook Called", ephemeral=True)


class Client(crescent.Client):
    async def on_crescent_command_error(
        self, exc: Exception, ctx: crescent.Context, was_handled: bool
    ) -> None:
        await ctx.respond(f"default command err handler called. was_handled={was_handled}")
        return await super().on_crescent_command_error(exc, ctx, was_handled)

    async def on_crescent_event_error(
        self, exc: Exception, event: hikari.Event, was_handled: bool
    ) -> None:
        print(f"default event err handler called. was_handled={was_handled}")
        return await super().on_crescent_event_error(exc, event, was_handled)

    async def on_crescent_autocomplete_error(
        self,
        exc: Exception,
        ctx: crescent.AutocompleteContext,
        inter: hikari.AutocompleteInteractionOption,
        was_handled: bool,
    ) -> None:
        print(f"default autcomplete err handler called. was_handled={was_handled}")
        return await super().on_crescent_autocomplete_error(exc, ctx, inter, was_handled)


async def bot_wide_hook(ctx: crescent.Context) -> None:
    await ctx.respond("Bot wide hook called")


bot = hikari.GatewayBot(os.getenv("TOKEN") or "")
client = Client(bot, command_hooks=[bot_wide_hook])

client.plugins.load("tests.test_bot.test_plugin")

group = crescent.Group("group", hooks=[myhook])
subgroup = group.sub_group("sub")


def normalize_name(name: str) -> str:
    if len(name) < 3:
        raise ValueError("Name must be at least 3 characters.")
    if len(name) > 32:
        raise ValueError("Name cannot be greater than 32 characters.")
    if not name[0].isalpha():
        raise ValueError("Name must start with a letter.")

    return name.lower()


async def fancy_validate_url(url: str) -> str:
    if url.startswith("https://"):
        return url

    await asyncio.sleep(1)
    raise ValueError("Our sophisticated validation has detected an invalid url.")


@client.include
@crescent.catch_command(ConverterException)
async def handle_converter_err(e: ConverterException, ctx: crescent.Context) -> None:
    await ctx.respond(repr(e))


@client.include
@crescent.command(name="converters", description="converters!")
class ConverterCommand:
    username = crescent.option(str, "username").convert(normalize_name)
    url1 = crescent.option(str, "url1").convert(fancy_validate_url)
    url2 = crescent.option(str, "url2").convert(fancy_validate_url)

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.respond(str((self.username, self.url1, self.url2)))


@client.include
@crescent.command(name="class-command", description="testing testing 123")
class ClassCommand:
    arg = crescent.option(str, "description")
    another_arg = crescent.option(str, name="another-arg")
    converted = crescent.option(str, name="str-to-num").convert(lambda v: int(v))

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.respond(f"{self.arg}, {self.another_arg}, {self.converted}: {type(self.converted)}")


@client.include
@crescent.command
async def reload_plugin(ctx: crescent.Context) -> None:
    client.plugins.load("tests.test_client.test_plugin", refresh=True)
    await ctx.respond("Done")


@client.include
@crescent.user_command(name="User")
async def user_command(ctx: crescent.Context, user: hikari.User) -> None:
    await ctx.respond(str(user))


@client.include
@crescent.message_command(name="Message")
async def msg_command(ctx: crescent.Context, msg: hikari.Message) -> None:
    await ctx.respond(str(msg))


class HandledErr(Exception):
    def __call__(self) -> None:
        super().__init__("Handled Exception")


class UnhandledErr(Exception):
    def __call__(self) -> None:
        super().__init__("Unhandled Exception")


@client.include
@crescent.catch_command(HandledErr)
async def handle_cmd_err(exc: HandledErr, ctx: crescent.Context) -> None:
    await ctx.respond(f"HandledErr raised in {ctx.command}: {exc!r}")


@client.include
@crescent.catch_event(HandledErr)
async def handle_event_err(exc: HandledErr, event: hikari.Event) -> None:
    print(f"HandledErr raised in {event}: {exc!r}")


@client.include
@crescent.catch_autocomplete(HandledErr)
async def handle_autocomplete_err(
    exc: HandledErr, ctx: crescent.AutocompleteContext, inter: hikari.AutocompleteInteractionOption
) -> None:
    print(f"HandledErr raised in {ctx.command}: {exc!r}")


# ERRORS!!!!!!!!!!
@client.include
@crescent.command
async def raise_err(ctx: crescent.Context) -> None:
    raise HandledErr()


@client.include
@crescent.command
async def raise_unhandled_err(ctx: crescent.Context) -> None:
    raise UnhandledErr()


@client.include
@crescent.event
async def on_message(event: hikari.MessageCreateEvent) -> None:
    if event.author.is_bot or not event.message.content:
        return

    if event.message.content == "!error":
        raise HandledErr()
    elif event.message.content == "!unhandled":
        raise UnhandledErr()
    elif event.message.content.startswith("!"):
        await event.message.respond("Use !error or !unhandled")


async def error_autocomplete(
    ctx: crescent.AutocompleteContext, option: hikari.AutocompleteInteractionOption
) -> Sequence[hikari.CommandChoice]:
    if option.value == "error":
        raise HandledErr()
    elif option.value == "unhandled":
        raise UnhandledErr()

    return [
        hikari.CommandChoice(name="error", value="error"),
        hikari.CommandChoice(name="unhandled", value="unhandled"),
    ]


async def autocomplete_response(
    ctx: crescent.AutocompleteContext, option: hikari.AutocompleteInteractionOption
) -> Sequence[hikari.CommandChoice]:
    return [hikari.CommandChoice(name="Some Option", value="1234")]


@client.include
@tasks.loop(seconds=5)
async def loop() -> None:
    print(f"LOOP: {datetime.now()}")


@client.include
@tasks.cronjob("* * * * *")
async def cron() -> None:
    print(f"CRON: {datetime.now()}")


if __name__ == "__main__":
    bot.run()
