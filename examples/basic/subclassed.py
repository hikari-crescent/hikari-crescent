import hikari
import crescent


class Bot(crescent.Bot):
    # Subclassed commands don't need to be included with `@bot.include`
    @crescent.command
    async def say(self, ctx: crescent.Context, word: str):
        await ctx.respond(word)

    @crescent.event
    async def event(self, event: hikari.ShardReadyEvent):
        print(event)


bot = Bot(token="TOKEN")
bot.run()
