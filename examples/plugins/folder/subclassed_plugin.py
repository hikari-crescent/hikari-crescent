import hikari
import crescent


class MyBot(hikari.GatewayBot):
    ...


# Subclassing `UserPlugin` allows you to use your own bot type for `plugin.app`
class MyPlugin(crescent.UserPlugin[MyBot]):
    ...


plugin = MyPlugin()
