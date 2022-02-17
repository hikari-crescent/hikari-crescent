import crescent

bot = crescent.Bot(token="TOKEN")

bot.plugins.load("plugin")
bot.plugins.load("folder.another_plugin")

bot.run()
