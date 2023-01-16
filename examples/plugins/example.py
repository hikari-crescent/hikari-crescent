import hikari
import crescent

bot = hikari.GatewayBot(token="...")
client = crescent.Client(bot)

client.plugins.load("plugin")
client.plugins.load("folder.another_plugin")

# Plugins can be unloaded and reloaded
client.plugins.unload("plugin")
client.plugins.load("plugin")

client.plugins.unload("folder.another_plugin")
client.plugins.load("folder.another_plugin")

bot.run()
