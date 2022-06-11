from __future__ import annotations

from hikari import MessageCreateEvent
from pytest import raises
from crescent.exceptions import PluginAlreadyLoadedError

from tests.crescent.plugins.plugin import (
    plugin,
    plugin_catch_command,
    plugin_command,
    plugin_event,
)
from tests.utils import MockBot


class TestPlugins:
    def test_load_plugin(self):
        bot = MockBot()

        _plugin = bot.plugins.load("tests.crescent.plugins.plugin")

        assert _plugin is plugin

        assert plugin_command in _plugin._children
        assert plugin_command.metadata.unique in bot._command_handler.registry

        assert plugin_event in _plugin._children
        # Length is one because only one event is listened to
        assert len(bot._event_manager.get_listeners(MessageCreateEvent)) == 1

        assert plugin_catch_command in _plugin._children
        assert plugin_catch_command in bot._command_error_handler.registry.values()

    def test_unload_plugin(self):
        bot = MockBot()

        bot.plugins.load("tests.crescent.plugins.plugin")
        bot.plugins.unload("tests.crescent.plugins.plugin")

        assert plugin_command.metadata.unique not in bot._command_handler.registry
        assert len(bot._event_manager.get_listeners(MessageCreateEvent)) == 0
        assert plugin_catch_command not in bot._command_error_handler.registry.values()

    def test_plugin_reload(self):
        bot = MockBot()

        bot.plugins.load("tests.crescent.plugins.plugin")
        bot.plugins.unload("tests.crescent.plugins.plugin")
        _plugin = bot.plugins.load("tests.crescent.plugins.plugin")

        assert _plugin is plugin

        assert plugin_command in _plugin._children
        assert plugin_command.metadata.unique in bot._command_handler.registry

        assert plugin_event in _plugin._children
        assert len(bot._event_manager.get_listeners(MessageCreateEvent)) == 1

        assert plugin_catch_command in _plugin._children
        assert plugin_catch_command in bot._command_error_handler.registry.values()

    def test_plugin_refresh(self):
        bot = MockBot()

        orig = bot.plugins.load("tests.crescent.plugins.plugin")
        bot.plugins.unload("tests.crescent.plugins.plugin")

        orig2 = bot.plugins.load("tests.crescent.plugins.plugin")

        # Calling refresh should automatically unload the plugin.
        new = bot.plugins.load("tests.crescent.plugins.plugin", refresh=True)

        assert orig is orig2
        assert orig is not new

    def test_load_hook(self):
        bot = MockBot()

        plugin = bot.plugins.load("tests.crescent.plugins.hook_plugin")
        assert plugin.loaded_hook_run_count == 1
        assert plugin.unloaded_hook_run_count == 0

        bot.plugins.unload("tests.crescent.plugins.hook_plugin")
        assert plugin.loaded_hook_run_count == 1
        assert plugin.unloaded_hook_run_count == 1

    def test_app_set(self):
        bot = MockBot()

        plugin = bot.plugins.load("tests.crescent.plugins.plugin")
        assert plugin._app is not None
        bot.plugins.unload("tests.crescent.plugins.plugin")
        assert plugin._app is None

    def test_load_twice(self):
        bot = MockBot()

        bot.plugins.load("tests.crescent.plugins.plugin")

        with raises(PluginAlreadyLoadedError):
            bot.plugins.load("tests.crescent.plugins.plugin")
