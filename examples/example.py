"""
Example of the public API.
Does do much right now.
"""

from crescent.bot import Bot
from crescent.commands.decorators import command
from crescent.commands.args import Description
from typing import Annotated


bot = Bot(
    "TOKEN",
    guilds=[750862883075915826]
)


@command(guild=750862883075915826)
def app_command(
    arg: Annotated[str, Description("Hello world!")],
    arg2: str = 10
):
    pass


bot.run()