# Classes are an alternitive syntax for commands. When you have a lot of arguments
# you can use them if you think its easier to read. Decorators above `@crescent.command`
# will work exactly the same as any other command.

import hikari

import crescent

bot = crescent.Bot(token="...")


@bot.include
@crescent.command(name="echo")
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
