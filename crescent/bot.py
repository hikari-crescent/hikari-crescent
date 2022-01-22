from __future__ import annotations

from concurrent.futures import Executor
from functools import partial
from itertools import chain
from typing import TYPE_CHECKING, Sequence, overload

from hikari import GatewayBot, Intents, ProxySettings, ShardReadyEvent, Snowflake
from hikari.config import CacheSettings, HTTPSettings

from crescent.commands.decorators import command as _command
from crescent.internal.app_command import AppCommandMeta
from crescent.internal.meta_struct import MetaStruct
from crescent.internal.registry import CommandHandler
from crescent.partial import Partial
from crescent.utils import iterate_vars


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

        self._command_handler = CommandHandler(self, guilds)
        self.default_guild = default_guild

        async def shard_ready(event: ShardReadyEvent):
            await self._command_handler.init(event)

        self.subscribe(
            ShardReadyEvent,
            shard_ready
        )

        for _, value in iterate_vars(self.__class__):
            if isinstance(value, Partial):
                value(self)
            if isinstance(value, MetaStruct):
                self._command_handler.register(value)

    def include(self, command: MetaStruct[AppCommandMeta] = None):
        if command is None:
            return self.include

        self._command_handler.register(command)

        return command

    def command(self, func=None, *args, **kwargs):
        if func is None:
            return partial(self.command, *args, **kwargs)
        return self.include(command=_command(func, *args, **kwargs))
