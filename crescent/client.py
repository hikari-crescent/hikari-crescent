from __future__ import annotations

from asyncio import create_task, get_running_loop
from contextlib import suppress
from functools import partial
from itertools import chain
from traceback import print_exception
from typing import TYPE_CHECKING, Protocol, overload, runtime_checkable

from hikari import AutocompleteInteraction, AutocompleteInteractionOption, CommandInteraction
from hikari import Event as hk_Event
from hikari import (
    InteractionCreateEvent,
    InteractionServerAware,
    PartialInteraction,
    RESTBotAware,
    Snowflakeish,
    StartedEvent,
)
from hikari.traits import EventManagerAware, RESTAware

from crescent.commands.hooks import add_hooks
from crescent.internal.handle_resp import handle_resp
from crescent.internal.includable import Includable
from crescent.internal.registry import CommandHandler, ErrorHandler
from crescent.plugin import PluginManager

if TYPE_CHECKING:
    from asyncio import Future
    from typing import Any, Awaitable, Callable, Coroutine, Sequence, TypeVar

    from hikari.api import InteractionResponseBuilder

    from crescent.context import AutocompleteContext, Context
    from crescent.typedefs import (
        AutocompleteErrorHandlerCallbackT,
        CommandErrorHandlerCallbackT,
        EventErrorHandlerCallbackT,
        HookCallbackT,
    )

    INCLUDABLE = TypeVar("INCLUDABLE", bound=Includable[Any])


__all__: Sequence[str] = ("Client", "GatewayTraits", "RESTTraits")


@runtime_checkable
class GatewayTraits(EventManagerAware, RESTAware, Protocol):
    """The traits crescent requires for a gateway-based bot."""


@runtime_checkable
class RESTTraits(InteractionServerAware, RESTAware, Protocol):
    """The base traits crescents requires for a REST-based bot."""


class Client:
    def __init__(
        self,
        app: RESTTraits | GatewayTraits,
        model: Any = None,
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
                Only works for gateway-based bots.
            command_hooks:
                List of hooks to run before all commands.
            command_after_hooks:
                List of hooks to run after all commands.
        """
        self.app = app
        self.model = model

        if update_commands:
            self._add_startup_callback(self.post_commands)
        self._add_startup_callback(self._on_start)

        if tracked_guilds is None:
            tracked_guilds = ()

        if default_guild and default_guild not in tracked_guilds:
            tracked_guilds = tuple(chain(tracked_guilds, (default_guild,)))

        self.allow_unknown_interactions = allow_unknown_interactions
        self.update_commands = update_commands

        self.command_hooks = command_hooks
        self.command_after_hooks = command_after_hooks

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

        self._started = False

        if isinstance(app, GatewayTraits):
            app.event_manager.subscribe(InteractionCreateEvent, self.on_interaction_event)
            return
        app.interaction_server.set_listener(
            CommandInteraction,  # pyright: ignore
            self.on_rest_interaction,  # type: ignore
        )
        app.interaction_server.set_listener(
            AutocompleteInteraction,  # type: ignore
            self.on_rest_interaction,  # type: ignore
        )

    async def on_rest_interaction(
        self, interaction: PartialInteraction
    ) -> InteractionResponseBuilder:
        future: Future[InteractionResponseBuilder] = get_running_loop().create_future()
        create_task(handle_resp(self, interaction, future))
        return await future

    async def on_interaction_event(self, event: InteractionCreateEvent) -> None:
        await handle_resp(self, event.interaction, None)

    def post_commands(self) -> Coroutine[Any, Any, None]:
        return self._command_handler.register_commands()

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

    def _run_future(self, callback: Coroutine[Any, Any, Any]) -> None:
        if self._started:
            get_running_loop().create_task(callback)
        else:
            self._add_startup_callback(lambda: callback)

    async def _on_start(self) -> None:
        self._started = True

    def _add_startup_callback(
        self, callback: Callable[[], Awaitable[None]]
    ) -> Callable[[], None] | None:
        async def on_start(_: Any) -> None:
            await callback()

        if isinstance(self.app, GatewayTraits):
            self.app.event_manager.subscribe(StartedEvent, on_start)
            return partial(self.app.event_manager.unsubscribe, StartedEvent, on_start)
        elif isinstance(self.app, RESTBotAware):
            self.app.add_startup_callback(on_start)
            return partial(self.app.remove_startup_callback, on_start)
        return None
