import hikari

import crescent

import random

bot = crescent.Bot(
    token="TOKEN",
    # This is the default guild for commands. You can set this to `None` in production
    # or not include the argument to post commands globally.
    default_guild=123456789123456789,
    # List of guilds that the bot compares its commands to. Guilds that aren't in this
    # list or are default_guild will not have their commands removed. If this is `None`
    # commands will be posted to all the guilds the bot is in.
    tracked_guilds=[987654321987654321],
)


@bot.include
@crescent.command(name="random")
class RandomNumber:
    max = crescent.option(int)

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.respond(random.randint(0, self.max))


@bot.include
@crescent.command(name="say")
class Say:
    to_say = crescent.option(str, "Make the bot say something", default="...", name="to-say")
    channel = crescent.option(hikari.GuildTextChannel, "The channel to send in", default=None)

    async def callback(self, ctx: crescent.Context) -> None:
        if self.channel is None:
            await ctx.app.rest.create_message(ctx.channel_id, self.to_say)

        else:
            await ctx.app.rest.create_message(self.channel.id, self.to_say)

        await ctx.respond("done", ephemeral=True)


bot.run()
