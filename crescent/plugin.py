from __future__ import annotations

from importlib import import_module, reload
from typing import TYPE_CHECKING, Dict

from crescent.internal.app_command import AppCommandMeta
from crescent.internal.meta_struct import MetaStruct

if TYPE_CHECKING:
    from typing import Any, Sequence, TypeVar

    from crescent.typedefs import HookCallbackT

    from .bot import Bot

    T = TypeVar("T", bound="MetaStruct[Any, Any]")


__all__: Sequence[str] = ("PluginManager", "Plugin")


class PluginManager:
    def __init__(self, bot: Bot) -> None:
        self.plugins: Dict[str, Plugin] = {}
        self._bot = bot

    def add_plugin(self, plugin: Plugin, force: bool = False) -> None:
        if plugin.name in self.plugins:
            if not force:
                raise ValueError(f"Plugin name {plugin.name} already exists.")
        self.plugins[plugin.name] = plugin
        plugin._setup(self._bot)

    def load(self, path: str, refresh: bool = False) -> Plugin:
        """Load a plugin from the module path.

        ```python
        import crescent

        bot = crescent.Bot(token=...)

        bot.plugins.load("folder.plugin")
        ```

        Args:
            path: The module path for the plugin.
            refresh: Whether or not to reload the plugin.
        """

        plugin = Plugin._from_module(path, refresh=refresh)
        self.add_plugin(plugin, force=refresh)
        return plugin


class Plugin:
    def __init__(
        self,
        name: str,
        command_hooks: list[HookCallbackT] | None = None,
        command_hook_after: list[HookCallbackT] | None = None,
    ) -> None:
        self.name = name
        self.command_hooks = command_hooks
        self.command_hook_after = command_hook_after
        self._children: list[MetaStruct[Any, Any]] = []

    def include(self, obj: T) -> T:
        if isinstance(obj.metadata, AppCommandMeta):
            if self.command_hooks:
                obj.metadata.hooks.extend(self.command_hooks)
            if self.command_hook_after:
                obj.metadata.after_hooks.extend(self.command_hook_after)
        self._children.append(obj)
        return obj

    def _setup(self, bot: Bot) -> None:
        for item in self._children:
            if isinstance(item.metadata, AppCommandMeta):
                if bot.command_hooks:
                    item.metadata.hooks.extend(bot.command_hooks)
                if bot.command_hook_after:
                    item.metadata.after_hooks.extend(bot.command_hook_after)
            item.register_to_app(bot)

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
