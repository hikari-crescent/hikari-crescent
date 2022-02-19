from __future__ import annotations

from asyncio import Task, create_task
from concurrent.futures import Executor
from itertools import chain
from traceback import print_exception
from typing import TYPE_CHECKING, cast, overload, Callable, Coroutine, Any

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

from crescent._ux import print_banner
from crescent.internal.handle_resp import handle_resp
from crescent.internal.meta_struct import MetaStruct
from crescent.internal.registry import CommandHandler, ErrorHandler
from crescent.plugin import PluginManager
from crescent.utils import iterate_vars

if TYPE_CHECKING:
    from typing import Dict, Optional, TypeVar, Union, Sequence

    from crescent.context import Context

    META_STRUCT = TypeVar("META_STRUCT", bound=MetaStruct)


__all___: Sequence[str] = "Bot"


class Bot(GatewayBot):

    __slots__: Sequence[str] = ("__dict__", "_command_handler", "default_guild")

    def __init__(
        self,
        token: str,
        *,
        tracked_guilds: Sequence[Snowflakeish] = None,
        default_guild: Optional[Snowflakeish] = None,
        update_commands: bool = True,
        allow_unknown_interactions: bool = False,
        allow_color: bool = True,
        banner: Optional[str] = "crescent",
        executor: Optional[Executor] = None,
        force_color: bool = False,
        cache_settings: Optional[CacheSettings] = None,
        http_settings: Optional[HTTPSettings] = None,
        intents: Intents = Intents.ALL_UNPRIVILEGED,
        logs: Union[None, int, str, Dict[str, Any]] = "INFO",
        max_rate_limit: float = 300,
        max_retries: int = 3,
        proxy_settings: Optional[ProxySettings] = None,
        rest_url: Optional[str] = None,
    ):
        """
        Crescent adds two parameters to Hikari's Gateway Bot. `tracked_guilds`
        and `default_guild`.

        Args:
            default_guild:
                The guild to post application commands to by default. If this is None,
                slash commands will be posted globall.
            tracked_guilds:
                The guilds to compare posted commands to. Commands will not be
                automatically removed from guilds that aren't in this list. This should
                be kept to as little guilds as possible to prevent rate limits.
        """
        super().__init__(
            token=token,
            allow_color=allow_color,
            banner=banner,
            executor=executor,
            force_color=force_color,
            cache_settings=cache_settings,
            http_settings=http_settings,
            intents=intents,
            logs=logs,
            max_rate_limit=max_rate_limit,
            max_retries=max_retries,
            proxy_settings=proxy_settings,
            rest_url=rest_url,
        )

        if tracked_guilds is None:
            tracked_guilds = ()

        if default_guild and default_guild not in tracked_guilds:
            tracked_guilds = tuple(chain(tracked_guilds, (default_guild,)))

        self.allow_unknown_interactions = allow_unknown_interactions
        self.update_commands = update_commands

        self._command_handler: CommandHandler = CommandHandler(self, tracked_guilds)
        self._error_handler = ErrorHandler(self)
        self.default_guild: Optional[Snowflakeish] = default_guild

        self._plugins = PluginManager(self)

        self.subscribe(ShardReadyEvent, self._on_shard_ready)
        self.subscribe(
            StartedEvent,
            cast(Callable[[StartedEvent], Coroutine[Any, Any, None]], self._on_started)
        )
        self.subscribe(InteractionCreateEvent, handle_resp)

        for _, value in iterate_vars(self.__class__):
            if isinstance(value, MetaStruct):
                value.register_to_app(self, self)

    async def _on_shard_ready(self, event: ShardReadyEvent):
        self._command_handler.application_id = event.application_id

    async def _on_started(self, _: StartedEvent) -> Optional[Task]:
        if self.update_commands:
            return create_task(self._command_handler.register_commands())
        return None

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

    @staticmethod
    def print_banner(banner: Optional[str], allow_color: bool, force_color: bool) -> None:
        print_banner(banner, allow_color, force_color)

    @property
    def plugins(self) -> PluginManager:
        return self._plugins

    async def on_crescent_error(self, exc: Exception, ctx: Context, was_handled: bool) -> None:
        if was_handled:
            return
        try:
            await ctx.respond("An unexpected error occurred.", ephemeral=True)
        except Exception:
            pass
        print(f"Unhandled exception occurred in the command {ctx.command}:")
        print_exception(exc.__class__, exc, exc.__traceback__)
