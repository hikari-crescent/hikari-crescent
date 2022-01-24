from __future__ import annotations

from concurrent.futures import Executor
from itertools import chain
from typing import TYPE_CHECKING, Sequence, overload

from hikari import (
    GatewayBot,
    Intents,
    InteractionCreateEvent,
    ProxySettings,
    ShardReadyEvent,
    Snowflake,
    CacheSettings,
    HTTPSettings,
)
from crescent.internal.meta_struct import MetaStruct
from crescent.internal.registry import CommandHandler
from crescent.internal.handle_resp import handle_resp
from crescent.utils import iterate_vars
from crescent.plugin import Plugin

if TYPE_CHECKING:
    from typing import Any, Dict, Optional, Union


__all___: Sequence[str] = (
    "Bot"
)


class Bot(GatewayBot):

    __slots__ = (
        "__dict__",
        "_command_handler",
        "default_guild",
    )

    @overload  # type: ignore
    def __init__(
        self,
        token: str, *,
        guilds: Sequence[Snowflake] = None,
        allow_color: bool = True,
        banner: Optional[str] = "hikari",
        executor: Optional[Executor] = None,
        force_color: bool = False,
        cache_settings: Optional[CacheSettings] = None,
        http_settings: Optional[HTTPSettings] = None,
        intents: Intents = ...,
        logs: Union[None, int, str, Dict[str, Any]] = "INFO",
        max_rate_limit: float = 300, max_retries: int = 3,
        proxy_settings: Optional[ProxySettings] = None,
        rest_url: Optional[str] = None
    ):
        ...

    def __init__(
        self,
        *args,
        default_guild: Optional[Snowflake] = None,
        guilds: Sequence[Snowflake] = None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        if guilds is None:
            guilds = ()

        if default_guild and default_guild not in guilds:
            guilds = tuple(chain(guilds, (default_guild,)))

        self._command_handler: CommandHandler = CommandHandler(self, guilds)
        self.default_guild: Optional[Snowflake] = default_guild
        self.plugins: Dict[str, Plugin] = {}

        async def shard_ready(event: ShardReadyEvent):
            await self._command_handler.init(event)

        self.subscribe(
            ShardReadyEvent,
            shard_ready
        )

        self.subscribe(
            InteractionCreateEvent,
            handle_resp
        )

        for _, value in iterate_vars(self.__class__):
            if isinstance(value, MetaStruct):
                value.register_to_app(
                    self,
                    self,
                    True
                )

    def include(self, command: MetaStruct[Any, Any] = None):
        if command is None:
            return self.include

        command.register_to_app(
            self,
            self,
            False,
        )

        return command

    def add_plugin(self, plugin: Plugin) -> None:
        if plugin.name in self.plugins:
            raise ValueError(f"Plugin name {plugin.name} already exists.")
        self.plugins[plugin.name] = plugin
        plugin.setup(self)

    def load_module(self, path: str) -> Plugin:
        plugin = Plugin._from_module(path)
        self.add_plugin(plugin)
        return plugin
