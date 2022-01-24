"""
Example showing the theoretical API
"""

import typing
import hikari
import crescent

bot = crescent.Bot(
    "TOKEN",
    # You can declare a default guild. If it is None, commands will be posted globally.
    # Can be overridden by manually specifying the guild.
    default_guild=12345678,
    # List of guilds you want to register guild commands to. I think this is required
    # to efficiently compare guild commands on the bot's startup.
    guilds=[12345678, 87654321, 92311421],
)


class MyBot(crescent.Bot):

    # Special event decorator that makes subclassing possible, although it will not be
    # required.
    @crescent.event
    def on_event(self, event: hikari.ShardReadyEvent):
        pass

    @crescent.command
    def say(
        self,
        ctx: crescent.Context,
        word: typing.Annotated[
            str,
            "This is an extremely long description that takes up more than one line because"
            "i think Annotated doesn't make it hard to write these.",
        ],
    ):
        # Command returns can be used
        return word


# Also declare commands outside class
# Read signiture to pass self and context
@bot.include
@crescent.command
def mycommand(self, ctx: crescent.Context):
    pass


# Once Hikari adds support
@bot.include
@crescent.user_command
def user_command(self, ctx, user):
    pass


@bot.include
@crescent.message_command
def message_command(self, ctx, user):
    pass


# Class based command system
@bot.include
@crescent.command
class Command:
    option_one = crescent.field(str, description="Hello world")
    option_one = crescent.field(int)

    def callback(self, ctx):
        pass
