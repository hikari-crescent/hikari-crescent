from __future__ import annotations

from importlib import import_module, reload
from logging import getLogger
from typing import TYPE_CHECKING

import hikari

from crescent.exceptions import PluginAlreadyLoadedError
from crescent.internal.meta_struct import MetaStruct
from crescent.utils import add_hooks

if TYPE_CHECKING:
    from typing import Any, Sequence, TypeVar

    from crescent.bot import Bot
    from crescent.typedefs import HookCallbackT, PluginCallbackT

    T = TypeVar("T", bound="MetaStruct[Any, Any]")


__all__: Sequence[str] = ("PluginManager", "Plugin")

_LOG = getLogger(__name__)


class PluginManager:
    def __init__(self, bot: Bot) -> None:
        self.plugins: dict[str, Plugin] = {}
        self._bot = bot

    def add_plugin(self, plugin: Plugin, force: bool = False) -> None:
        _LOG.warning("`add_plugin` is deprecated and will be removed in a future release.")

        self._add_plugin("", plugin, refresh=force)

    def unload(self, path: str) -> None:
        plugin = self.plugins.pop(path)
        plugin._unload()

    def load(self, path: str, refresh: bool = False) -> Plugin:
        """Load a plugin from the module path.

        ```python
        import crescent

        bot = crescent.Bot(token=...)

        bot.plugins.load("folder.plugin")
        ```

        Args:
            path: The module path for the plugin.
            refresh: Whether or not to reload the plugin and the plugin's module.
        """

        if refresh:
            old_plugin = self.plugins.pop(path)
            old_plugin._unload()

        plugin = Plugin._from_module(path, refresh=refresh)
        self._add_plugin(path, plugin, refresh=refresh)

        return plugin

    def _add_plugin(self, path: str, plugin: Plugin, refresh: bool = False) -> None:
        if path in self.plugins and not refresh:
            raise PluginAlreadyLoadedError(
                f"Plugin `{path}` is already loaded."
                " Add the kwarg `refresh=True` to the function call if this is intended."
            )

        self.plugins[path] = plugin
        plugin._load(self._bot)


class Plugin:
    def __init__(
        self,
        name: str | None = None,
        *,
        command_hooks: list[HookCallbackT] | None = None,
        command_after_hooks: list[HookCallbackT] | None = None,
    ) -> None:
        if name is not None:
            _LOG.warning(
                "Pluin option `name` is deprecated and will be removed in a future release."
            )

        self.command_hooks = command_hooks
        self.command_after_hooks = command_after_hooks
        self._app: Bot | None = None
        self._children: list[MetaStruct[Any, Any]] = []

        self._load_hooks: list[PluginCallbackT] = []
        self._unload_hooks: list[PluginCallbackT] = []

    def include(self, obj: T) -> T:
        add_hooks(self, obj)
        self._children.append(obj)
        return obj

    def load_hook(self, callback: PluginCallbackT) -> None:
        self._load_hooks.append(callback)

    def unload_hook(self, callback: PluginCallbackT) -> None:
        self._unload_hooks.append(callback)

    def _load(self, bot: Bot) -> None:
        self._app = bot

        for callback in self._load_hooks:
            callback()
        for child in self._children:
            add_hooks(bot, child)
            child.register_to_app(bot)

        bot.subscribe(hikari.StoppedEvent, self._on_bot_close)

    def _unload(self) -> None:
        assert self._app
        self._app.unsubscribe(hikari.StoppedEvent, self._on_bot_close)
        self._app = None

        for callback in self._unload_hooks:
            callback()

        for child in self._children:
            for hook in child.plugin_unload_hooks:
                hook(child)

    async def _on_bot_close(self, bot: Bot) -> None:
        self._unload()

    @classmethod
    def _from_module(cls, path: str, refresh: bool = False) -> Plugin:
        parents = path.split(".")

        name = parents.pop(-1)
        package = ".".join(parents)
        if package:
            name = "." + name
        module = import_module(name, package)
        if refresh:
            module = reload(module)
        plugin = getattr(module, "plugin", None)
        if not isinstance(plugin, Plugin):
            raise ValueError(
                f"Plugin {path} has no `plugin` or `plugin` is not of type Plugin. "
                "If you want to name your plugin something else, you have to add an "
                "alias (plugin = YOUR_PLUGIN_NAME)."
            )

        return plugin
