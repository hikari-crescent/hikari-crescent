from __future__ import annotations

from asyncio import Event as aio_Event
from asyncio import Task, create_task
from contextlib import suppress
from itertools import chain
from traceback import print_exception
from typing import TYPE_CHECKING, Protocol, overload

from hikari import AutocompleteInteractionOption
from hikari import Event as hk_Event
from hikari import InteractionCreateEvent, ShardReadyEvent, Snowflakeish, StartedEvent
from hikari.traits import EventManagerAware, RESTAware

from crescent.commands.hooks import add_hooks
from crescent.internal.handle_resp import active_clients, handle_resp
from crescent.internal.includable import Includable
from crescent.internal.registry import CommandHandler, ErrorHandler
from crescent.plugin import PluginManager

if TYPE_CHECKING:
    from typing import Any, Callable, Sequence, TypeVar

    from crescent.context import AutocompleteContext, Context
    from crescent.typedefs import (
        AutocompleteErrorHandlerCallbackT,
        CommandErrorHandlerCallbackT,
        EventErrorHandlerCallbackT,
        HookCallbackT,
    )

    INCLUDABLE = TypeVar("INCLUDABLE", bound=Includable[Any])


__all___: Sequence[str] = ("Client", "GatewayTraits")


class GatewayTraits(EventManagerAware, RESTAware, Protocol):
    """The traits crescent requires for a bot."""


class Client:
    def __init__(
        self,
        app: GatewayTraits,
        *,
        tracked_guilds: Sequence[Snowflakeish] | None = None,
        default_guild: Snowflakeish | None = None,
        update_commands: bool = True,
        allow_unknown_interactions: bool = False,
        command_hooks: list[HookCallbackT] | None = None,
        command_after_hooks: list[HookCallbackT] | None = None,
    ):
        """
        Args:
            app:
                The hikari bot instance.
            tracked_guilds:
                The guilds to compare posted commands to. Commands will not be
                automatically removed from guilds that aren't in this list. This should
                be kept to as little guilds as possible to prevent rate limits.
            default_guild:
                The guild to post application commands to by default. If this is None,
                slash commands will be posted globally.
            update_commands:
                If `True` or not specified, update commands when the bot starts.
            command_hooks:
                List of hooks to run before all commands.
            command_after_hooks:
                List of hooks to run after all commands.
        """
        active_clients[id(app)] = self

        self.app = app

        if tracked_guilds is None:
            tracked_guilds = ()

        if default_guild and default_guild not in tracked_guilds:
            tracked_guilds = tuple(chain(tracked_guilds, (default_guild,)))

        self.allow_unknown_interactions = allow_unknown_interactions
        self.update_commands = update_commands

        self.command_hooks = command_hooks
        self.command_after_hooks = command_after_hooks

        self._started = aio_Event()

        self._command_handler: CommandHandler = CommandHandler(self, tracked_guilds)

        self._command_error_handler: ErrorHandler[
            CommandErrorHandlerCallbackT[Any]
        ] = ErrorHandler()
        self._event_error_handler: ErrorHandler[EventErrorHandlerCallbackT[Any]] = ErrorHandler()
        self._autocomplete_error_handler: ErrorHandler[
            AutocompleteErrorHandlerCallbackT[Any]
        ] = ErrorHandler()

        self.default_guild: Snowflakeish | None = default_guild

        self._plugins = PluginManager(self)

        app.event_manager.subscribe(ShardReadyEvent, self._on_shard_ready)

        async def on_started(event: StartedEvent) -> None:
            self._started.set()
            await self._on_started(event)

        app.event_manager.subscribe(StartedEvent, on_started)
        app.event_manager.subscribe(InteractionCreateEvent, handle_resp)

    async def _on_shard_ready(self, event: ShardReadyEvent) -> None:
        self._command_handler._application_id = event.application_id

    async def _on_started(self, _: StartedEvent) -> Task[None] | None:
        if self.update_commands:
            return create_task(self._command_handler.register_commands())
        return None

    @property
    def started(self) -> aio_Event:
        """
        Returns `asyncio.Event` that is set when `hikari.StartedEvent` is dispatched.
        """
        return self._started

    @overload
    def include(self, command: INCLUDABLE) -> INCLUDABLE:
        ...

    @overload
    def include(self, command: None = ...) -> Callable[[INCLUDABLE], INCLUDABLE]:
        ...

    def include(
        self, command: INCLUDABLE | None = None
    ) -> INCLUDABLE | Callable[[INCLUDABLE], INCLUDABLE]:
        if command is None:
            return self.include

        add_hooks(self, command)

        command.register_to_client(self)

        return command

    @property
    def plugins(self) -> PluginManager:
        return self._plugins

    @property
    def commands(self) -> CommandHandler:
        return self._command_handler

    async def on_crescent_command_error(
        self, exc: Exception, ctx: Context, was_handled: bool
    ) -> None:
        if was_handled:
            return
        with suppress(Exception):
            await ctx.respond("An unexpected error occurred.", ephemeral=True)
        print(f"Unhandled exception occurred in the command {ctx.command}:")
        print_exception(exc.__class__, exc, exc.__traceback__)

    async def on_crescent_event_error(
        self, exc: Exception, event: hk_Event, was_handled: bool
    ) -> None:
        if was_handled:
            return
        print(f"Unhandled exception occurred for {type(event)}:")
        print_exception(exc.__class__, exc, exc.__traceback__)

    async def on_crescent_autocomplete_error(
        self,
        exc: Exception,
        ctx: AutocompleteContext,
        option: AutocompleteInteractionOption,
        was_handled: bool,
    ) -> None:
        if was_handled:
            return
        print(
            f"Unhandled exception occurred in the autocomplete interaction for {ctx.command}"
            f" (option: {option.name}):"
        )
        print_exception(exc.__class__, exc, exc.__traceback__)
