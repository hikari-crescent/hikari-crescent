"""
Example of the public API.
Does do much right now.
"""

from typing import Union

import hikari
from typing_extensions import Annotated

import crescent

bot = crescent.Bot(token="TOKEN", default_guild=778289112381784115)

bot.load_module("plugin")

group = crescent.Group("my_group")
sub_group = group.sub_group("my_sub_group")


@bot.include
@crescent.command(guild=778289112381784115)
async def app_command(
    ctx: crescent.Context,
    arg: Annotated[str, crescent.Description("Hello world!")],
    arg2: int = 10,
):
    await ctx.respond("Hello")


@bot.include
@group
@crescent.command
async def sub_command(ctx):
    pass


@bot.include
@sub_group
@crescent.command
async def sub_sub_command(ctx):
    pass


@bot.include
@crescent.event
async def event(event: hikari.ShardReadyEvent):
    print(event)


@bot.include
@crescent.command(name="echo")
class Say:
    to_say = crescent.option(str, "Make the bot say something", default="...")
    channel = crescent.option(
        hikari.GuildTextChannel, "The channel to send in", default=None
    )

    async def callback(self, ctx: crescent.Context) -> None:
        if self.channel is None:
            await ctx.app.rest.create_message(int(ctx.channel_id), self.to_say)

        else:
            await ctx.app.rest.create_message(int(self.channel), self.to_say)

        await ctx.respond("done", ephemeral=True)


bot.run()
