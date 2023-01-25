from __future__ import annotations

from importlib import import_module, reload
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generic, Literal, Sequence, TypeVar, cast, overload

from crescent.commands.hooks import add_hooks
from crescent.exceptions import PluginAlreadyLoadedError
from crescent.internal.includable import Includable

if TYPE_CHECKING:
    from crescent.client import Client, GatewayTraits, RESTTraits
    from crescent.typedefs import HookCallbackT, PluginCallbackT

__all__: Sequence[str] = ("PluginManager", "Plugin")


T = TypeVar("T", bound="Includable[Any]")

# NOTE: When mypy supports PEP 696 (type var defaults) a `default="GatewayTraits"` kwarg
# should be added to improve ergonomics.
BotT = TypeVar("BotT", bound="GatewayTraits | RESTTraits")
ModelT = TypeVar("ModelT")


_LOG = getLogger(__name__)


class PluginManager:
    def __init__(self, client: Client) -> None:
        self.plugins: dict[str, Plugin[Any, Any]] = {}
        self._client = client

    @overload
    def load(self, path: str, /, *, refresh: bool = ...) -> Plugin[Any, Any]:
        ...

    @overload
    def load(self, path: str, *, strict: Literal[True], refresh: bool = ...) -> Plugin[Any, Any]:
        ...

    @overload
    def load(
        self, path: str, *, strict: Literal[False], refresh: bool = ...
    ) -> Plugin[Any, Any] | None:
        ...

    @overload
    def load(self, path: str, refresh: bool = ..., strict: bool = ...) -> Plugin[Any, Any] | None:
        ...

    def load(
        self, path: str, refresh: bool = False, strict: bool = True
    ) -> Plugin[Any, Any] | None:
        """Load a plugin from the module path.

        ```python
        import crescent

        bot = crescent.Bot(token=...)

        bot.plugins.load("folder.plugin")
        ```

        Args:
            path: The module path for the plugin.
            refresh: Whether or not to reload the plugin and the plugin's module.
            strict:
                If false, the function will not error when module file does not have a plugin
                variable.
        """

        if refresh:
            old_plugin = self.plugins.pop(path)
            old_plugin._unload()

        plugin: Plugin[Any, Any] | None = Plugin._from_module(path, refresh=refresh, strict=strict)
        if not plugin:
            return None
        self._add_plugin(path, plugin, refresh=refresh)

        return plugin

    def load_folder(
        self, path: str, refresh: bool = False, strict: bool = True
    ) -> list[Plugin[Any, Any]]:
        """Loads plugins from a folder.

        ```python
        import crescent
        import hikari

        bot = hikari.GatewayBot(token=...)
        client = crescent.Client(bot)

        client.plugins.load("project.plugin_folder")
        ```

        If a file is attempted to be loaded that does not have a plugin variable,
        a `ValueError` will be raised. Files who's names start with an underscore
        will not be loaded.

        Args:
            path: The path to the folder that contains the plugins.
            refresh: Whether or not to reload the plugin and the plugin's module.
            strict:
                If false, the function will not error when a file does not have a plugin
                variable.
        Returns:
            A list of plugins that were loaded.
        """

        pathlib_path = Path(*path.split("."))
        loaded_plugins: list[Plugin[Any, Any]] = []
        loaded_paths: list[str] = []

        for glob_path in pathlib_path.glob(r"**/[!_]*.py"):
            self._load_plugin_from_filepath(
                path=glob_path,
                plugins=loaded_plugins,
                paths=loaded_paths,
                refresh=refresh,
                strict=strict,
            )

        if not loaded_plugins:
            _LOG.warning(
                "No plugins were loaded! Are you sure `%s` is the correct directory?", pathlib_path
            )

        return loaded_plugins

    def _load_plugin_from_filepath(
        self,
        path: Path,
        plugins: list[Plugin[Any, Any]],
        paths: list[str],
        *,
        strict: bool,
        refresh: bool,
    ) -> None:
        mod_name = ".".join(path.as_posix()[:-3].split("/"))
        try:
            if maybe_plugin := self.load(mod_name, refresh=refresh, strict=strict):
                plugins.append(maybe_plugin)
                paths.append(mod_name)
        except ValueError as e:
            for plugin_path in paths:
                self.unload(plugin_path)
            raise e

    def _add_plugin(self, path: str, plugin: Plugin[Any, Any], refresh: bool = False) -> None:
        if path in self.plugins and not refresh:
            raise PluginAlreadyLoadedError(
                f"Plugin `{path}` is already loaded."
                " Add the kwarg `refresh=True` to the function call if this is intended."
            )

        self.plugins[path] = plugin
        plugin._load(self._client)

    def unload(self, path: str) -> None:
        """
        Unload a plugin.

        Args:
            path: The module path for the plugin.
        """
        plugin = self.plugins.pop(path)
        plugin._unload()

    def unload_all(self) -> None:
        """
        Unload all of the plugins that are currently loaded.
        """
        for path in tuple(self.plugins.keys()):
            self.unload(path)


class Plugin(Generic[BotT, ModelT]):
    def __init__(
        self,
        *,
        command_hooks: list[HookCallbackT] | None = None,
        command_after_hooks: list[HookCallbackT] | None = None,
    ) -> None:
        self.command_hooks = command_hooks
        self.command_after_hooks = command_after_hooks
        self._client: Client | None = None
        self._model: ModelT | None = None
        self._children: list[Includable[Any]] = []

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

    @property
    def app(self) -> BotT:
        if not self._client:
            raise AttributeError("`Plugin.app` can not be accessed before the plugin is loaded.")
        return cast(BotT, self._client.app)

    @property
    def model(self) -> ModelT:
        if not self._client:
            raise AttributeError("`Plugin.model` can not be accessed before the plugin is loaded.")
        return cast(ModelT, self._client.model)

    @property
    def client(self) -> Client:
        if not self._client:
            raise AttributeError(
                "`Plugin.client` can not be accessed before the plugin is loaded."
            )
        return self._client

    def _load(self, client: Client) -> None:
        self._client = client

        for callback in self._load_hooks:
            callback()
        for child in self._children:
            add_hooks(client, child)
            child.register_to_client(client)

    def _unload(self) -> None:
        for callback in self._unload_hooks:
            callback()

        for child in self._children:
            for hook in child.plugin_unload_hooks:
                hook(child)

        self._client = None

    @overload
    @classmethod
    def _from_module(cls, path: str, /, *, refresh: bool = ...) -> Plugin[BotT, ModelT]:
        ...

    @overload
    @classmethod
    def _from_module(
        cls, path: str, *, strict: Literal[True], refresh: bool = ...
    ) -> Plugin[BotT, ModelT]:
        ...

    @overload
    @classmethod
    def _from_module(
        cls, path: str, *, strict: Literal[False], refresh: bool = ...
    ) -> Plugin[BotT, ModelT] | None:
        ...

    @overload
    @classmethod
    def _from_module(
        cls, path: str, refresh: bool = ..., strict: bool = ...
    ) -> Plugin[BotT, ModelT] | None:
        ...

    @classmethod
    def _from_module(
        cls, path: str, refresh: bool = False, strict: bool = True
    ) -> Plugin[BotT, ModelT] | None:
        parents = path.split(".")

        name = parents.pop(-1)
        package = ".".join(parents)
        if package:
            name = "." + name
        module = import_module(name, package)
        if refresh:
            module = reload(module)
        plugin: Plugin[BotT, ModelT] | None = getattr(module, "plugin", None)
        if strict and not plugin:
            raise ValueError(
                f"Plugin {path} has no `plugin` or `plugin` is not of type Plugin. "
                "If you want to name your plugin something else, you have to add an "
                "alias (plugin = YOUR_PLUGIN_NAME)."
            )

        return plugin
