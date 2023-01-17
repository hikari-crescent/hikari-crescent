from __future__ import annotations

from hikari import MessageCreateEvent
from pytest import LogCaptureFixture, raises

from crescent.exceptions import PluginAlreadyLoadedError
from tests.crescent.plugins.plugin import (
    plugin,
    plugin_catch_command,
    plugin_command,
    plugin_event,
)
from tests.utils import MockClient, arrays_contain_same_elements


class TestPlugins:
    def test_load_plugin(self):
        client = MockClient()

        _plugin = client.plugins.load("tests.crescent.plugins.plugin")

        assert _plugin is plugin

        assert plugin_command in _plugin._children
        assert plugin_command.metadata.unique in client._command_handler._registry

        assert plugin_event in _plugin._children
        # Length is one because only one event is listened to
        assert len(client.app._event_manager.get_listeners(MessageCreateEvent)) == 1

        assert plugin_catch_command in _plugin._children
        assert plugin_catch_command in client._command_error_handler.registry.values()

    def test_load_not_plugin(self):
        client = MockClient()

        with raises(ValueError):
            client.plugins.load("tests.crescent.plugins.not_plugin")

        plugin = client.plugins.load("tests.crescent.plugins.not_plugin", strict=False)
        assert not plugin

    def test_unload_plugin(self):
        client = MockClient()

        client.plugins.load("tests.crescent.plugins.plugin")
        client.plugins.unload("tests.crescent.plugins.plugin")

        assert plugin_command.metadata.unique not in client._command_handler._registry
        assert len(client.app._event_manager.get_listeners(MessageCreateEvent)) == 0
        assert plugin_catch_command not in client._command_error_handler.registry.values()

    def test_plugin_reload(self):
        client = MockClient()

        client.plugins.load("tests.crescent.plugins.plugin")
        client.plugins.unload("tests.crescent.plugins.plugin")
        _plugin = client.plugins.load("tests.crescent.plugins.plugin")

        assert _plugin is plugin

        assert plugin_command in _plugin._children
        assert plugin_command.metadata.unique in client._command_handler._registry

        assert plugin_event in _plugin._children
        assert len(client.app._event_manager.get_listeners(MessageCreateEvent)) == 1

        assert plugin_catch_command in _plugin._children
        assert plugin_catch_command in client._command_error_handler.registry.values()

    def test_plugin_refresh(self):
        client = MockClient()

        orig = client.plugins.load("tests.crescent.plugins.plugin")
        client.plugins.unload("tests.crescent.plugins.plugin")

        orig2 = client.plugins.load("tests.crescent.plugins.plugin")

        # Calling refresh should automatically unload the plugin.
        new = client.plugins.load("tests.crescent.plugins.plugin", refresh=True)

        assert orig is orig2
        assert orig is not new

    def test_load_folder(self, caplog: LogCaptureFixture):
        client = MockClient()

        plugins = client.plugins.load_folder("tests.crescent.plugins.plugin_folder")

        from tests.crescent.plugins.plugin_folder.plugin import plugin
        from tests.crescent.plugins.plugin_folder.plugin_subfolder.plugin import (
            plugin as nested_plugin,
        )

        # Only the -OO warning should be logged if plugins are loaded successfully.
        assert len(caplog.messages) == 1

        assert arrays_contain_same_elements([plugin, nested_plugin], plugins)
        assert arrays_contain_same_elements(
            [plugin, nested_plugin], client.plugins.plugins.values()
        )

    def test_load_folder_refresh(self):
        client = MockClient()

        client.plugins.load_folder("tests.crescent.plugins.plugin_folder")

        with raises(PluginAlreadyLoadedError):
            client.plugins.load_folder("tests.crescent.plugins.plugin_folder", refresh=False)

        client.plugins.load_folder("tests.crescent.plugins.plugin_folder", refresh=True)

    def test_load_folder_with_not_plugins(self):
        client = MockClient()

        with raises(ValueError):
            client.plugins.load_folder("tests.crescent.plugins.plugin_folder_not_strict")

        # Plugins should be empty after loading fails
        assert not client.plugins.plugins

        plugins = client.plugins.load_folder(
            "tests.crescent.plugins.plugin_folder_not_strict", strict=False
        )

        from tests.crescent.plugins.plugin_folder_not_strict.plugin import plugin

        assert arrays_contain_same_elements([plugin], plugins)

    def test_load_dir_not_exists(self, caplog: LogCaptureFixture):
        client = MockClient()

        client.plugins.load_folder("does.not.exist")

        assert (
            caplog.messages[-1]
            == "No plugins were loaded! Are you sure `does/not/exist` is the correct directory?"
        )

    def test_load_hook(self):
        client = MockClient()

        plugin = client.plugins.load("tests.crescent.plugins.hook_plugin")
        assert plugin.loaded_hook_run_count == 1
        assert plugin.unloaded_hook_run_count == 0

        client.plugins.unload("tests.crescent.plugins.hook_plugin")
        assert plugin.loaded_hook_run_count == 1
        assert plugin.unloaded_hook_run_count == 1

    def test_app_set(self):
        client = MockClient()

        plugin = client.plugins.load("tests.crescent.plugins.plugin")
        assert plugin._client is not None
        client.plugins.unload("tests.crescent.plugins.plugin")
        assert plugin._client is None

    def test_load_twice(self):
        client = MockClient()

        client.plugins.load("tests.crescent.plugins.plugin")

        with raises(PluginAlreadyLoadedError):
            client.plugins.load("tests.crescent.plugins.plugin")

    def test_client_loaded(self):
        client = MockClient()

        plugin = client.plugins.load("tests.crescent.plugins.plugin")

        plugin.app

    def test_client_not_loaded(self):
        client = MockClient()

        plugin = client.plugins.load("tests.crescent.plugins.plugin")
        client.plugins.unload("tests.crescent.plugins.plugin")

        with raises(AttributeError):
            plugin.app
