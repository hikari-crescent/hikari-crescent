import hikari

import crescent
import dataclasses

bot = hikari.GatewayBot(token="...")


@dataclasses.dataclass
class Model:
    value = 5


# The modal kwarg is optional. If provided, you can access this object through `plugin.model`.
client = crescent.Client(bot, model=Model())

client.plugins.load("plugin")
client.plugins.load("folder.another_plugin")

# Plugins can be unloaded and reloaded
client.plugins.unload("plugin")
client.plugins.load("plugin")

client.plugins.unload("folder.another_plugin")
client.plugins.load("folder.another_plugin")

bot.run()
