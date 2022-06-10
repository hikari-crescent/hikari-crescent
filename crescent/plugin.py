from __future__ import annotations

from importlib import import_module, reload
from typing import TYPE_CHECKING

from crescent.internal.meta_struct import MetaStruct
from crescent.utils import add_hooks

if TYPE_CHECKING:
    from typing import Any, Sequence, TypeVar

    from crescent.typedefs import HookCallbackT

    from .bot import Bot

    T = TypeVar("T", bound="MetaStruct[Any, Any]")


__all__: Sequence[str] = ("PluginManager", "Plugin")


class PluginManager:
    def __init__(self, bot: Bot) -> None:
        self.plugins: dict[str, Plugin] = {}
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
        command_after_hooks: list[HookCallbackT] | None = None,
    ) -> None:
        self.name = name
        self.command_hooks = command_hooks
        self.command_after_hooks = command_after_hooks
        self._children: list[MetaStruct[Any, Any]] = []

    def include(self, obj: T) -> T:
        add_hooks(self, obj)
        self._children.append(obj)
        return obj

    def _setup(self, bot: Bot) -> None:
        for item in self._children:
            add_hooks(bot, item)
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
