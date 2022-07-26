# Depending on whether a slash command or user command is used in a dms or guilds, you
# can either receive a `hikari.User` or `hikari.Member` object for users respectively.
# `hikari.Member` is a subclass of `hikari.User`.

import crescent
import hikari


bot = crescent.Bot(token="...")


# This slash command is enabled in dms so user is not guaranteed to be a `hikari.Member`
# object.
# Crescent will prevent you from typing this command with `hikari.Member` because that
# violates type safety.
@bot.include
@crescent.command(dm_enabled=True)  # `dm_enabled=True` is default.
async def slash_command(ctx: crescent.Context, user: hikari.User):
    ...


# This slash command can only be used in guilds. That ensures that every user will be a
# `hikari.Member` object.
@bot.include
@crescent.command(dm_enabled=False)
async def guild_only_slash_command(ctx: crescent.Context, user: hikari.Member):
    ...


# User commands must always be typed with `hikari.User`. This is because calling a user
# command from a guild on a user that left that guild will result in a `hikari.User`
# object. This makes it impossible to guarantee that a user will ever be a `hikari.Member`
# object.
# Crescent will not prevent you from typing a user command with `hikari.Member` but it is
# not type safe so your type checker will complain.
@bot.include
@crescent.user_command(dm_enabled=True)  # `dm_enabled=True` is default.
async def user_command(ctx: crescent.Context, user: hikari.User):
    ...


@bot.include
@crescent.user_command(dm_enabled=False)
async def guild_only_user_command(ctx: crescent.Context, user: hikari.User):
    ...


bot.run()
