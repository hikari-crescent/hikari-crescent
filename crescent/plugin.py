from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Dict, Tuple

from crescent.internal.app_command import AppCommandMeta
from crescent.internal.meta_struct import MetaStruct

if TYPE_CHECKING:
    from typing import Sequence, TypeVar

    from crescent.typedefs import HookCallbackT

    from .bot import Bot

    T = TypeVar("T", bound="MetaStruct")


__all__: Sequence[str] = ("PluginManager", "Plugin")


class PluginManager:
    def __init__(self, bot: Bot) -> None:
        self.plugins: Dict[str, Plugin] = {}
        self._bot = bot

    def add_plugin(self, plugin: Plugin) -> None:
        if plugin.name in self.plugins:
            raise ValueError(f"Plugin name {plugin.name} already exists.")
        self.plugins[plugin.name] = plugin
        plugin._setup(self._bot)

    def load(self, path: str) -> Plugin:
        """Load a plugin from the module path.

        ```python
        import crescent

        bot = crescent.Bot(token=...)

        bot.plugins.load("folder.plugin")
        ```

        Args:
            path: The module path for the plugin.

        """
        plugin = Plugin._from_module(path)
        self.add_plugin(plugin)
        return plugin


class Plugin:
    def __init__(self, name: str, command_hooks: list[HookCallbackT]) -> None:
        self.name = name
        self.command_hooks = command_hooks
        self._children: list[Tuple[MetaStruct, bool]] = []

        for value in vars(self.__class__).values():
            if isinstance(value, MetaStruct):
                if isinstance(value.metadata, AppCommandMeta):
                    value.metadata.hooks.extend(self.command_hooks)
                self._children.append((value, True))

    def include(self, obj: T) -> T:
        if isinstance(obj.metadata, AppCommandMeta):
            obj.metadata.hooks.extend(self.command_hooks)
        self._children.append((obj, False))
        return obj

    def _setup(self, bot: Bot) -> None:
        for item, is_method in self._children:
            item.register_to_app(bot, self if is_method else None)

    @classmethod
    def _from_module(cls, path: str) -> Plugin:
        parents = path.split(".")

        name = parents.pop(-1)
        package = ".".join(parents)
        if package:
            name = "." + name
        module = import_module(name, package)
        plugin = getattr(module, "plugin", None)
        if not isinstance(plugin, Plugin):
            raise ValueError(
                f"Plugin {path} has no `plugin` or `plugin` is not of type Plugin. "
                "If you want to name your plugin something else, you have to add an "
                "alias (plugin = YOUR_PLUGIN_NAME)."
            )

        return plugin
