from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Tuple

from crescent.internal.meta_struct import MetaStruct

if TYPE_CHECKING:
    from typing import TypeVar

    from .bot import Bot

    T = TypeVar("T", bound="MetaStruct")


class Plugin:
    def __init__(self, name: str) -> None:
        self.name = name
        self._children: list[Tuple[MetaStruct, bool]] = []

        for value in vars(self.__class__).values():
            if isinstance(value, MetaStruct):
                self._children.append((value, True))

    def include(self, obj: T) -> T:
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
