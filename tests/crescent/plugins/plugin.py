# This plugin is loaded by the `test_plugins.py` tests

from hikari import MessageCreateEvent
from crescent import Plugin, event, catch_command, command, Context

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
