import os
from datetime import datetime
from typing import Sequence

import dotenv
import hikari
from typing_extensions import Annotated

import crescent
from crescent.ext import tasks

dotenv.load_dotenv()


async def myhook(ctx: crescent.Context) -> None:
    await ctx.respond("Hook Called", ephemeral=True)


class Bot(crescent.Bot):
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
        ctx: crescent.Context,
        inter: hikari.AutocompleteInteractionOption,
        was_handled: bool,
    ) -> None:
        print(f"default autcomplete err handler called. was_handled={was_handled}")
        return await super().on_crescent_autocomplete_error(exc, ctx, inter, was_handled)


async def bot_wide_hook(ctx: crescent.Context) -> None:
    await ctx.respond("Bot wide hook called")


bot = Bot(
    os.environ["TOKEN"], default_guild=int(os.environ["GUILD"]), command_hooks=[bot_wide_hook]
)

bot.plugins.load("tests.test_bot.test_plugin")

group = crescent.Group("group", hooks=[myhook])
subgroup = group.sub_group("sub")


@bot.include
@crescent.command(name="class-command", description="testing testing 123")
class ClassCommand:
    arg = crescent.option(str, "description")
    another_arg = crescent.option(str, name="another-arg")

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.respond(f"{self.arg}, {self.another_arg}")


@bot.include
@crescent.command
async def command(ctx: crescent.Context, arg: str) -> None:
    await ctx.respond(arg)


@bot.include
@crescent.command
async def reload_plugin(ctx: crescent.Context) -> None:
    ctx.app.plugins.load("tests.test_bot.test_plugin", refresh=True)
    await ctx.respond("Done")


@bot.include
@group.child
@crescent.command
async def group_command(ctx: crescent.Context, arg: str) -> None:
    await ctx.respond(arg)


@bot.include
@subgroup.child
@crescent.hook(myhook)
@crescent.command
async def subgroup_command(ctx: crescent.Context, arg: str) -> None:
    await ctx.respond(arg)


@bot.include
@crescent.user_command(name="User")
async def user_command(ctx: crescent.Context, user: hikari.User) -> None:
    await ctx.respond(str(user))


@bot.include
@crescent.message_command(name="Message")
async def msg_command(ctx: crescent.Context, msg: hikari.Message) -> None:
    await ctx.respond(str(msg))


class HandledErr(Exception):
    def __call__(self) -> None:
        super().__init__("Handled Exception")


class UnhandledErr(Exception):
    def __call__(self) -> None:
        super().__init__("Unhandled Exception")


@bot.include
@crescent.catch_command(HandledErr)
async def handle_cmd_err(exc: HandledErr, ctx: crescent.Context) -> None:
    await ctx.respond(f"HandledErr raised in {ctx.command}: {exc!r}")


@bot.include
@crescent.catch_event(HandledErr)
async def handle_event_err(exc: HandledErr, event: hikari.Event) -> None:
    print(f"HandledErr raised in {event}: {exc!r}")


@bot.include
@crescent.catch_autocomplete(HandledErr)
async def handle_autocomplete_err(
    exc: HandledErr, ctx: crescent.Context, inter: hikari.AutocompleteInteractionOption
) -> None:
    print(f"HandledErr raised in {ctx.command}: {exc!r}")


# ERRORS!!!!!!!!!!
@bot.include
@crescent.command
async def raise_err(ctx: crescent.Context) -> None:
    raise HandledErr()


@bot.include
@crescent.command
async def raise_unhandled_err(ctx: crescent.Context) -> None:
    raise UnhandledErr()


@bot.include
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
    ctx: crescent.Context, option: hikari.AutocompleteInteractionOption
) -> Sequence[hikari.CommandChoice]:
    if option.value == "error":
        raise HandledErr()
    elif option.value == "unhandled":
        raise UnhandledErr()

    return [
        hikari.CommandChoice(name="error", value="error"),
        hikari.CommandChoice(name="unhandled", value="unhandled"),
    ]


@bot.include
@crescent.command
async def error_autocomplete_command(
    ctx: crescent.Context, option: Annotated[str, crescent.Autocomplete(error_autocomplete)]
) -> None:
    await ctx.respond(option)



async def autocomplete_response(
    ctx: crescent.Context, option: hikari.AutocompleteInteractionOption
) -> Sequence[hikari.CommandChoice]:
    return [hikari.CommandChoice(name="Some Option", value="1234")]


@bot.include
@crescent.command
async def autocomplete_interaction(
    ctx: crescent.Context, result: Annotated[str, crescent.Autocomplete(autocomplete_response)]
) -> None:
    await ctx.respond(result, ephemeral=True)


@bot.include
@tasks.loop(seconds=5)
async def loop() -> None:
    print(f"LOOP: {datetime.now()}")


@bot.include
@tasks.cronjob("* * * * *")
async def cron() -> None:
    print(f"CRON: {datetime.now()}")


if __name__ == "__main__":
    bot.run()
