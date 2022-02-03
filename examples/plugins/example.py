import crescent

bot = crescent.Bot(token="TOKEN")

bot.load_module("plugin")
bot.load_module("folder.another_plugin")

bot.run()
