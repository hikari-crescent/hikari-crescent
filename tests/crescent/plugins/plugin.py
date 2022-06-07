# This plugin is loaded by the `test_plugins.py` tests

from hikari import MessageCreateEvent

from crescent import Context, Plugin, catch_command, command, event

plugin = Plugin("test-plugin")


@plugin.include
@command
async def plugin_command(ctx: Context):
    ...


@plugin.include
@event
async def plugin_event(event: MessageCreateEvent):
    ...


@plugin.include
@catch_command(Exception)
async def plugin_catch_command(exc: Exception, ctx: Context):
    ...
