import crescent

bot = crescent.Bot(token="TOKEN")

bot.plugins.load("plugin")
bot.plugins.load("folder.another_plugin")

# Plugins can be unloaded and reloaded
bot.plugins.unload("plugin")
bot.plugins.load("plugin")

bot.plugins.unload("folder.another_plugin")
bot.plugins.load("folder.another_plugin")

bot.run()
