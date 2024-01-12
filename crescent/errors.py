from __future__ import annotations

from typing import Any, Awaitable, Callable, Sequence, TypeVar

from crescent.internal.includable import Includable
from crescent.typedefs import (
    AutocompleteErrorHandlerCallbackT,
    CommandErrorHandlerCallbackT,
    EventErrorHandlerCallbackT,
)

__all__: Sequence[str] = ("catch_command", "catch_event", "catch_autocomplete")


T = TypeVar("T", bound=Callable[..., Awaitable[Any]])


def _make_catch_function(
    error_handler_var: str, supports_custom_ctx: bool = False
) -> Callable[[type[Exception]], Callable[[T], Includable[T]]]:
    def func(*exceptions: type[Exception]) -> Callable[[T], Includable[T]]:
        def app_set_hook(includable: Includable[Any]) -> None:
            for exc in exceptions:
                getattr(includable.client, error_handler_var).register(includable, exc)

        def plugin_unload_hook(includable: Includable[Any]) -> None:
            for exc in exceptions:
                getattr(includable.client, error_handler_var).remove(exc)

        def decorator(callback: Any) -> Includable[Any]:
            includable = Includable(
                callback, client_set_hooks=[app_set_hook], plugin_unload_hooks=[plugin_unload_hook]
            )

            return includable

        return decorator

    return func


_catch_command = _make_catch_function("_command_error_handler", supports_custom_ctx=True)
_catch_event = _make_catch_function("_event_error_handler")
_catch_autocomplete = _make_catch_function("_autocomplete_error_handler", supports_custom_ctx=True)


# NOTE: These functions are defined to help properly type the user facings functions and
# so linters view the catch decorators as a function instead of a variable


def catch_command(
    *exceptions: type[Exception],
) -> Callable[[CommandErrorHandlerCallbackT[Any]], Includable[CommandErrorHandlerCallbackT[Any]]]:
    """
    Catch an exception or subclasses of an exception passed into this function when the
    exception is raised in a command.

    ### Example
    ```python
    @client.include
    @crescent.catch_command(Exception)
    async def handler(exc: Exception, ctx: crescent.Context) -> None:
        await ctx.respond(f"{exc} raised in {ctx.command}!")

    @client.include
    @crescent.command
    async def example_command(ctx: crescent.Context):
        ...
    ```
    """
    return _catch_command(*exceptions)


def catch_event(
    *exceptions: type[Exception],
) -> Callable[[EventErrorHandlerCallbackT[Any]], Includable[EventErrorHandlerCallbackT[Any]]]:
    """
    Catch an exception or subclasses of an exception passed into this function when the
    exception is raised in an event.

    ### Example
    ```python
    @client.include
    @crescent.catch_event(Exception)
    async def handler(exc: Exception, event: hikari.Event) -> None:
        print(f"{exc} raised in {event}!")

    @client.include
    @crescent.event
    async def example_error(event: hikari.MessageCreateEvent) -> None:
        raise Exception
    ```
    """
    return _catch_event(*exceptions)


def catch_autocomplete(
    *exceptions: type[Exception],
) -> Callable[
    [AutocompleteErrorHandlerCallbackT[Any]], Includable[AutocompleteErrorHandlerCallbackT[Any]]
]:
    """
    Catch an exception or subclasses of an exception passed into this function when the
    exception is raised in an autocomplete handler.

    ### Example
    ```python
    @client.include
    @crescent.catch_autocomplete(Exception)
    async def on_autocomplete_random_error(
        exc: Exception,
        ctx: crescent.AutocompleteContext,
        inter: hikari.AutocompleteInteractionOption,
    ) -> None:
        print(f"{exc} raised in autocomplete for {ctx.command}!")

    # An autocomplete callback that a command is using.
    async def example_autocomplete(
        ctx: crescent.AutocompleteContext, option: hikari.AutocompleteInteractionOption
    ) -> list[tuple[str, str]]:
        raise Exception
    ```
    """
    return _catch_autocomplete(*exceptions)
