"""
Example of the public API.
Does do much right now.
"""

from typing import Annotated
import crescent
import hikari


bot = crescent.Bot(
    "TOKEN",
    guilds=[750862883075915826]
)


@bot.command(guild=750862883075915826)
def app_command(
    ctx: crescent.Context,
    arg: Annotated[str, crescent.Description("Hello world!")],
    arg2: str = 10
):
    ctx.create_initial_response(
        content="Hello world!",
        response_type=hikari.ResponseType.MESSAGE_CREATE,
    )


bot.run()
