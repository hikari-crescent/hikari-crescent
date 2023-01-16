import hikari

import crescent

import random

# The bot object can be any impl that implements `hikari.traits.RESTAware` and
# `hikari.traits.EventManagerAware`. For most users this will be `hikari.GatewayBot`.
bot = hikari.GatewayBot(token="TOKEN")
# The client object controls all the features of crescent.
client = crescent.Client(bot)


@client.include
@crescent.command(name="random")
class RandomNumber:
    max = crescent.option(int)

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.respond(random.randint(0, self.max))


@client.include
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
