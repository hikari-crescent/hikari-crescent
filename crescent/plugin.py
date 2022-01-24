from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypeVar

    from .bot import Bot
    from .internal.meta_struct import MetaStruct

    T = TypeVar("T", bound="MetaStruct")


class Plugin:
    def __init__(self, name: str) -> None:
        self.name = name
        self._children: list[MetaStruct] = []

    def include(self, obj: T) -> T:
        self._children.append(obj)
        return obj

    def _setup(self, bot: Bot) -> None:
        for item in self._children:
            bot.include(item)

    @classmethod
    def _from_module(cls, path: str) -> Plugin:
        parents = path.split(".")
        module = import_module(
            parents.pop(0),
            ".".join(parents),
        )
        plugin = getattr(module, "plugin", None)
        if not isinstance(plugin, Plugin):
            raise ValueError(
                f"Plugin {path} has no `plugin` or `plugin` is not of type Plugin. "
                "If you want to name your plugin something else, you have to add an "
                "alias (plugin = YOUR_PLUGIN_NAME)."
            )

        return plugin
