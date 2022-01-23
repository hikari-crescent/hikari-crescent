"""
Example of the public API.
Does do much right now.
"""

from typing import Annotated

from hikari import ResponseType
from crescent.bot import Bot
from crescent.commands.decorators import command
from crescent.commands.args import Description
from crescent.context import Context


bot = Bot(
    "TOKEN",
    guilds=[750862883075915826]
)


@command(guild=750862883075915826)
def app_command(
    ctx: Context,
    arg: Annotated[str, Description("Hello world!")],
    arg2: str = 10
):
    ctx.create_initial_response(
        content="Hello world!",
        response_type=ResponseType.MESSAGE_CREATE,
    )


bot.run()
