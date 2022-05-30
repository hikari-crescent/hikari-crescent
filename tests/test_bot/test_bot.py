import os
from typing import Sequence

import dotenv
import hikari
from typing_extensions import Annotated

import crescent

dotenv.load_dotenv()


async def myhook(ctx: crescent.Context) -> None:
    await ctx.respond("Hook Called", ephemeral=True)


class Bot(crescent.Bot):
    async def on_crescent_error(
        self, exc: Exception, ctx: crescent.Context, was_handled: bool
    ) -> None:
        await ctx.respond(f"default err handler called. was_handled={was_handled}")
        return await super().on_crescent_error(exc, ctx, was_handled)


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
async def handle_err(exc: HandledErr, ctx: crescent.Context) -> None:
    await ctx.respond(f"HandledErr raised in {ctx.command}: {exc!r}")


@bot.include
@crescent.command
async def raise_err(ctx: crescent.Context) -> None:
    raise HandledErr()


@bot.include
@crescent.command
async def raise_unhandled_err(ctx: crescent.Context) -> None:
    raise UnhandledErr()


@bot.include
@crescent.command(deprecated=True)
async def deprecated_command(ctx: crescent.Context) -> None:
    pass


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


if __name__ == "__main__":
    bot.run()
