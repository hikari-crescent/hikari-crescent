"""
Example of the public API.
Does do much right now.
"""

import typing
import crescent
import hikari


bot = crescent.Bot(
    "TOKEN",
    guilds=[750862883075915826]
)

group = crescent.Group("my_group")
sub_group = group.sub_group("my_sub_group")


@bot.include
@crescent.command(guild=750862883075915826)
def app_command(
    ctx: crescent.Context,
    arg: typing.Annotated[str, crescent.Description("Hello world!")],
    arg2: str = 10
):
    ctx.create_initial_response(
        content="Hello world!",
        response_type=hikari.ResponseType.MESSAGE_CREATE,
    )


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


bot.run()
