import os

import dotenv
import hikari

import crescent

dotenv.load_dotenv()


async def myhook(ctx: crescent.Context) -> None:
    await ctx.respond("Hook Called", ephemeral=True)


class Bot(crescent.Bot):
    @crescent.user_command(name="Subclassed User")
    async def sc_user(self, ctx: crescent.Context, user: hikari.User):
        assert isinstance(self, Bot)
        await ctx.respond(str(user))

    @crescent.message_command(name="Subclassed Message")
    async def sc_msg(self, ctx: crescent.Context, msg: hikari.Message):
        assert isinstance(self, Bot)
        await ctx.respond(str(msg))

    @crescent.hook(myhook)
    @crescent.command
    async def subclassed_command(self, ctx: crescent.Context) -> None:
        assert isinstance(self, Bot)
        await ctx.respond("works")

    async def on_crescent_error(
        self, exc: Exception, ctx: crescent.Context, was_handled: bool
    ) -> None:
        await ctx.respond(
            f"default err handler called. was_handled={was_handled}"
        )
        return await super().on_crescent_error(exc, ctx, was_handled)


bot = Bot(os.getenv("TOKEN"), default_guild=int(os.getenv("GUILD")))


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
@crescent.catch(HandledErr)
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


bot.run()
