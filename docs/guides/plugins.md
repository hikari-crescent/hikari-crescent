# Plugins

Plugins are used to split your bot into multiple files. Plugins require your bot to be
packaged, so it is recommended to follow this structure. You can see an example of this
structure in the [crescent template](https://github.com/hikari-crescent/template).

```
working_directory/
    bot/
        __main__.py
        plugins/
            plugin_a.py
            plugin_b.py
```

The `__main__.py` file is where you create your client. It would look something
like this:

```python
import crescent
import hikari

bot = hikari.GatewayBot("YOUR_TOKEN_HERE")
client = crescent.Client(bot)

bot.run()
```

Now to load plugins, simply use the `bot.plugins.load_folder` function.

```python
bot = hikari.GatewayBot("YOUR_TOKEN_HERE")
client = crescent.Client(bot)

client.plugins.load_folder("bot.plugins")

bot.run()
```

When you run your bot with `python -m bot` from `working_directory`, plugins
will be loaded on startup.

!!! note
     The path that is used to load plugins is relative to the directory
     you are running the bot from.

## Inside a plugin file

In the inside of your plugin file you create a plugin class. You can use
`@plugin.include` to add a command to your bot exactly the same way you
would with `@bot.include`. The `plugin` variable must be called `plugin`.

```python
plugin = crescent.Plugin[hikari.GatewayBot, None]()

@plugin.include
@crescent.command
class plugin_command:
    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.respond("Inside a plugin")
```

If you need to access your bot class inside a plugin file, you can use the
`plugin.app` attribute. Accessing this attribute will raise an exception if
the plugin is not yet loaded.

```python
plugin = crescent.Plugin[hikari.GatewayBot, None]()

@plugin.include
@crescent.command
class plugin_command:
    async def callback(self, ctx: crescent.Context) -> None:
        print(plugin.app)  # <crescent.bot.Bot object at 0x????????????>
        ...
```

## Hooks

Plugins allow you run to run functions when they are loaded and unloaded.

```python
plugin = crescent.Plugin[hikari.GatewayBot, None]()

@plugin.load_hook
def load():
    print("The plugin is loaded")

@plugin.unload_hook
def unload():
    print("The plugin is unloaded")
```


## Type Safe `plugin.app`

If you are using a inherited bot class you can change generics on `crescent.Plugin` so
`plugin.app` is typed with your class.

```python
import typing

class MyBot(hikari.GatewayBot):
    ...

MyPlugin = crescent.Plugin[MyBot, None]

typing.reveal_type(MyPlugin().app)  # `MyBot`
```
