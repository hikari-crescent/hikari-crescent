from __future__ import annotations

from asyncio import get_running_loop
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

from crescent.hooks import add_hooks
from crescent.internal.handle_resp import handle_resp
from crescent.internal.includable import Includable
from crescent.internal.registry import CommandHandler, ErrorHandler
from crescent.plugin import PluginManager
from crescent.typedefs import EventHookCallbackT
from crescent.utils import create_task

if TYPE_CHECKING:
    from asyncio import Future
    from typing import Any, Awaitable, Callable, Coroutine, Sequence, TypeVar

    from hikari.api import InteractionResponseBuilder

    from crescent.context import AutocompleteContext, Context
    from crescent.typedefs import (
        AutocompleteErrorHandlerCallbackT,
        CommandErrorHandlerCallbackT,
        CommandHookCallbackT,
        EventErrorHandlerCallbackT,
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
    """
    The client object is a wrapper around your bot that lets you use
    Crescent's features.

    ### Example

    ```python
    import hikari
    import crescent

    bot = hikari.GatewayBot("your token")
    client = crescent.Client(bot)

    # Crescent's features can be used.
    @client.include
    @crescent.command
    async def ping(ctx: crescent.Context):
        await ctx.respong("Pong")

    bot.run()
    ```
    """

    def __init__(
        self,
        app: RESTTraits | GatewayTraits,
        model: Any = None,
        *,
        tracked_guilds: Sequence[Snowflakeish] | None = None,
        default_guild: Snowflakeish | None = None,
        update_commands: bool = True,
        allow_unknown_interactions: bool = False,
        command_hooks: list[CommandHookCallbackT] | None = None,
        command_after_hooks: list[CommandHookCallbackT] | None = None,
        event_hooks: list[EventHookCallbackT[hk_Event]] | None = None,
        event_after_hooks: list[EventHookCallbackT[hk_Event]] | None = None,
    ):
        """
        Args:
            app:
                The hikari bot instance.
            model:
                An object to store global data. This object can be accessed
                with the `Plugin.model` property.

                ### Example

                ```python
                # In bot.py
                bot = hikari.GatewayBot("your token")
                client = crescent.Client(bot, "I am a model")

                client.plugins.load("plugin")

                # In plugin.py
                plugin = crescent.Plugin()

                @plugin.on_load
                def on_load():
                    # Print the model object that was set earlier to the console.
                    print(plugin.model)  # prints "I am a model"
                ```

                If no model is set, the model will default to `None`.

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
            self._add_startup_callback(self._post_commands)
        self._add_startup_callback(self._on_start)

        if tracked_guilds is None:
            tracked_guilds = ()

        if default_guild and default_guild not in tracked_guilds:
            tracked_guilds = tuple(chain(tracked_guilds, (default_guild,)))

        self.allow_unknown_interactions = allow_unknown_interactions
        self.update_commands = update_commands

        self.command_hooks: list[CommandHookCallbackT] = command_hooks or []
        self.command_after_hooks: list[CommandHookCallbackT] = command_after_hooks or []
        self.event_hooks: list[EventHookCallbackT[hk_Event]] = event_hooks or []
        self.event_after_hooks: list[EventHookCallbackT[hk_Event]] = event_after_hooks or []

        self._command_handler: CommandHandler = CommandHandler(self, tracked_guilds)

        self._command_error_handler: ErrorHandler[CommandErrorHandlerCallbackT[Any]] = (
            ErrorHandler()
        )
        self._event_error_handler: ErrorHandler[EventErrorHandlerCallbackT[Any]] = ErrorHandler()
        self._autocomplete_error_handler: ErrorHandler[AutocompleteErrorHandlerCallbackT[Any]] = (
            ErrorHandler()
        )

        self.default_guild: Snowflakeish | None = default_guild

        self._plugins = PluginManager(self)

        self._started = False

        if isinstance(app, GatewayTraits):
            app.event_manager.subscribe(InteractionCreateEvent, self._on_interaction_event)
            return
        app.interaction_server.set_listener(
            CommandInteraction,  # pyright: ignore
            self._on_rest_interaction,  # type: ignore
        )
        app.interaction_server.set_listener(
            AutocompleteInteraction,  # type: ignore
            self._on_rest_interaction,  # type: ignore
        )

    async def _on_rest_interaction(
        self, interaction: PartialInteraction
    ) -> InteractionResponseBuilder:
        future: Future[InteractionResponseBuilder] = get_running_loop().create_future()
        create_task(handle_resp(self, interaction, future))
        return await future

    async def _on_interaction_event(self, event: InteractionCreateEvent) -> None:
        await handle_resp(self, event.interaction, None)

    def _post_commands(self) -> Coroutine[Any, Any, None]:
        return self._command_handler.register_commands()

    @overload
    def include(self, obj: INCLUDABLE) -> INCLUDABLE: ...

    @overload
    def include(self, obj: None = ...) -> Callable[[INCLUDABLE], INCLUDABLE]: ...

    def include(
        self, obj: INCLUDABLE | None = None
    ) -> INCLUDABLE | Callable[[INCLUDABLE], INCLUDABLE]:
        """
        Register an includable object, such as an event or command handler.

        ### Example

        ```python
        client = crescent.Client(...)

        @client.include
        @crescent.command
        async def ping(ctx: crescent.Context):
            await ctx.respong("Pong")
        ```
        """
        if obj is None:
            return self.include

        add_hooks(
            obj,
            self.command_hooks,
            self.command_after_hooks,
            self.event_hooks,
            self.event_after_hooks,
        )

        obj.register_to_client(self)

        return obj

    @property
    def plugins(self) -> PluginManager:
        """
        Return the plugin manager object. This object lets you load and unload
        plugins. See `PluginManager` for more information.
        """
        return self._plugins

    @property
    def commands(self) -> CommandHandler:
        """
        Return the command handler object. This object lets you access command
        information that is not normally accessible. See `CommandHandler` for
        more information.
        """
        return self._command_handler

    async def on_crescent_command_error(
        self, exc: Exception, ctx: Context, was_handled: bool
    ) -> None:
        """
        This function is run when there is an error in a crescent command
        that is not caught with any error handlers. You can inherit from this
        class and override this function to change default error handling.
        """
        if was_handled:
            return
        with suppress(Exception):
            await ctx.respond("An unexpected error occurred.", ephemeral=True)
        print(f"Unhandled exception occurred in the command {ctx.command}:")
        print_exception(exc.__class__, exc, exc.__traceback__)

    async def on_crescent_event_error(
        self, exc: Exception, event: hk_Event, was_handled: bool
    ) -> None:
        """
        This function is run when there is an error in a crescent event
        that is not caught with any error handlers. You can inherit from this
        class and override this function to change default error handling.
        """
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
        """
        This function is run when there is an error in an autocomplete handler
        that is not caught with any error handlers. You can inherit from this
        class and override this function to change default error handling.
        """
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
