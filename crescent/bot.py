from __future__ import annotations
from asyncio import ensure_future

from concurrent.futures import Executor
from typing import TYPE_CHECKING, Sequence, overload

from hikari import GatewayBot, Intents, ProxySettings, ShardReadyEvent, Snowflake
from hikari.config import CacheSettings, HTTPSettings
from crescent.internal.registry import CommandHandler
from crescent.partial import Partial
from crescent.utils import iterate_vars


if TYPE_CHECKING:
    from typing import Any, Dict, Optional, Union


__all___: Sequence[str] = (
    "Bot"
)


class Bot(GatewayBot):

    __slots__ = (*GatewayBot.__slots__, "__dict__")

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
        guilds: Sequence[Snowflake] = None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        if guilds is None:
            guilds = ()

        async def shard_ready(event: ShardReadyEvent):
            print(event)
            await CommandHandler.init(self, guilds, event)

        self.subscribe(
            ShardReadyEvent,
            shard_ready
        )

        for _, value in iterate_vars(self.__class__):
            if isinstance(value, Partial):
                value(self)
