from __future__ import annotations

from typing_extensions import Annotated  # Python 3.8

# If you're using Python 3.9+, use this import instead:
# from typing import Annotated

import hikari
import crescent


bot = crescent.Bot(token="...")


@bot.include
@crescent.command
async def say(ctx: crescent.Context, word: str) -> None:
    await ctx.respond(f"{ctx.user.username} said {word}")


@bot.include
@crescent.command
async def add(
    ctx: crescent.Context,
    first_number: Annotated[int, "This is a description", crescent.MaxValue(50)],
    second_number: Annotated[
        int,
        crescent.Choices(
            hikari.CommandChoice(name="Choice", value=123),
            hikari.CommandChoice(name="Choice2", value=456),
            hikari.CommandChoice(name="Choice3", value=789),
        ),
    ],
) -> None:
    await ctx.respond(f"{first_number} + {second_number} = {first_number + second_number}")


@bot.include
@crescent.user_command
async def my_user_command(ctx: crescent.Context, user: hikari.User | hikari.Member) -> None:
    await ctx.respond(f"Hello {user.username}")


@bot.include
@crescent.message_command
async def my_message_command(ctx: crescent.Context, message: hikari.Message) -> None:
    await ctx.respond(f'The message said "{message.content}"')


@bot.include
@crescent.event
async def event(event: hikari.ShardReadyEvent) -> None:
    print(event)


bot.run()
