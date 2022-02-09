import os

import dotenv
import crescent

dotenv.load_dotenv()


bot = crescent.Bot(
    os.getenv("TOKEN"),
    default_guild=int(os.getenv("GUILD")),
)


group = crescent.Group("group")
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
@crescent.command
async def subgroup_command(ctx: crescent.Context, arg: str) -> None:
    await ctx.respond(arg)


bot.run()
