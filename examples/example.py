"""
Example of the public API.
Does do much right now.
"""

import typing

import hikari

import crescent

bot = crescent.Bot("TOKEN", guilds=[750862883075915826])

bot.load_module("plugin")

group = crescent.Group("my_group")
sub_group = group.sub_group("my_sub_group")


@bot.include
@crescent.command(guild=750862883075915826)
async def app_command(
    ctx: crescent.Context,
    arg: typing.Annotated[str, crescent.Description("Hello world!")],
    arg2: str = 10,
):
    await ctx.respond("Hello")


@bot.include
@group
@crescent.command
def sub_command(ctx):
    pass


@bot.include
@sub_group
@crescent.command
def sub_sub_command(ctx):
    pass


@bot.include
@crescent.event
def event(event: hikari.ShardReadyEvent):
    print(event)


bot.run()
