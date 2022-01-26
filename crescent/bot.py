from __future__ import annotations

from concurrent.futures import Executor
from itertools import chain
from typing import TYPE_CHECKING, Callable, Sequence, overload

from hikari import (
    CacheSettings,
    GatewayBot,
    HTTPSettings,
    Intents,
    InteractionCreateEvent,
    ProxySettings,
    ShardReadyEvent,
    Snowflakeish,
    StartedEvent,
)

from crescent.internal.handle_resp import handle_resp
from crescent.internal.meta_struct import MetaStruct
from crescent.internal.registry import CommandHandler
from crescent.plugin import Plugin
from crescent.utils import iterate_vars

if TYPE_CHECKING:
    from typing import Any, Dict, Optional, TypeVar, Union

    META_STRUCT = TypeVar("META_STRUCT", bound=MetaStruct)


__all___: Sequence[str] = "Bot"


class Bot(GatewayBot):

    __slots__ = (
        "__dict__",
        "_command_handler",
        "default_guild",
    )

    @overload  # type: ignore
    def __init__(
        self,
        token: str,
        *,
        tracked_guilds: Sequence[Snowflakeish] = None,
        default_guild: Optional[Snowflakeish] = None,
        allow_color: bool = True,
        banner: Optional[str] = "hikari",
        executor: Optional[Executor] = None,
        force_color: bool = False,
        cache_settings: Optional[CacheSettings] = None,
        http_settings: Optional[HTTPSettings] = None,
        intents: Intents = ...,
        logs: Union[None, int, str, Dict[str, Any]] = "INFO",
        max_rate_limit: float = 300,
        max_retries: int = 3,
        proxy_settings: Optional[ProxySettings] = None,
        rest_url: Optional[str] = None,
    ):
        ...

    def __init__(
        self,
        *args,
        tracked_guilds: Sequence[Snowflakeish] = None,
        default_guild: Optional[Snowflakeish] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        if tracked_guilds is None:
            tracked_guilds = ()

        if default_guild and default_guild not in tracked_guilds:
            tracked_guilds = tuple(chain(tracked_guilds, (default_guild,)))

        self._command_handler: CommandHandler = CommandHandler(self, tracked_guilds)
        self.default_guild: Optional[Snowflakeish] = default_guild
        self.plugins: Dict[str, Plugin] = {}

        async def shard_ready(event: ShardReadyEvent):
            self._command_handler.application_id = event.application_id

        async def started(_: StartedEvent):
            await self._command_handler.register_commands()

        self.subscribe(ShardReadyEvent, shard_ready)
        self.subscribe(StartedEvent, started)

        self.subscribe(InteractionCreateEvent, handle_resp)

        for _, value in iterate_vars(self.__class__):
            if isinstance(value, MetaStruct):
                value.register_to_app(self, self)

    @overload
    def include(self, command: META_STRUCT) -> META_STRUCT:
        ...

    @overload
    def include(self, command: None = ...) -> Callable[[META_STRUCT], META_STRUCT]:
        ...

    def include(self, command: META_STRUCT | None = None):
        if command is None:
            return self.include

        command.register_to_app(app=self)

        return command

    def add_plugin(self, plugin: Plugin) -> None:
        if plugin.name in self.plugins:
            raise ValueError(f"Plugin name {plugin.name} already exists.")
        self.plugins[plugin.name] = plugin
        plugin._setup(self)

    def load_module(self, path: str) -> Plugin:
        plugin = Plugin._from_module(path)
        self.add_plugin(plugin)
        return plugin
