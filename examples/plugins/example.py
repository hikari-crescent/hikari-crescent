import crescent

bot = crescent.Bot(token="TOKEN")

bot.plugins.load("plugin")
bot.plugins.load("folder.another_plugin")

# Plugins can be unloaded and reloaded
bot.plugins.unload("example")  # Uses plugin name
bot.plugins.load("plugin")  # Uses plugin path

bot.run()
