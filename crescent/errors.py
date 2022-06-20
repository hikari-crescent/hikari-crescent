from __future__ import annotations

from typing import Any, Awaitable, Callable, Sequence, TypeVar

from crescent.internal.meta_struct import MetaStruct
from crescent.typedefs import (
    AutocompleteErrorHandlerCallbackT,
    CommandErrorHandlerCallbackT,
    EventErrorHandlerCallbackT,
)

__all__: Sequence[str] = ("catch_command", "catch_event", "catch_autocomplete")


T = TypeVar("T", bound=Callable[..., Awaitable[Any]])


def _make_catch_function(
    error_handler_var: str,
) -> Callable[[type[Exception]], Callable[[T], MetaStruct[T, Any]]]:
    def func(*exceptions: type[Exception]) -> Callable[[T], MetaStruct[T, Any]]:
        def app_set_hook(meta: MetaStruct[T, Any]) -> None:
            for exc in exceptions:
                getattr(meta.app, error_handler_var).register(meta, exc)

        def plugin_unload_hook(meta: MetaStruct[T, Any]) -> None:
            for exc in exceptions:
                getattr(meta.app, error_handler_var).remove(exc)

        def decorator(callback: T) -> MetaStruct[T, Any]:
            meta = MetaStruct(
                callback,
                None,
                app_set_hooks=[app_set_hook],
                plugin_unload_hooks=[plugin_unload_hook],
            )

            return meta

        return decorator

    return func


_catch_command = _make_catch_function("_command_error_handler")
_catch_event = _make_catch_function("_event_error_handler")
_catch_autocomplete = _make_catch_function("_autocomplete_error_handler")


# NOTE: These functions are defined to help properly type the user facings functions and
# so linters view the catch decorators as a function instead of a variable


def catch_command(
    *exceptions: type[Exception],
) -> Callable[
    [CommandErrorHandlerCallbackT[Any]], MetaStruct[CommandErrorHandlerCallbackT[Any], Any],
]:
    return _catch_command(*exceptions)


def catch_event(
    *exceptions: type[Exception],
) -> Callable[
    [EventErrorHandlerCallbackT[Any]], MetaStruct[EventErrorHandlerCallbackT[Any], Any],
]:
    return _catch_event(*exceptions)


def catch_autocomplete(
    *exceptions: type[Exception],
) -> Callable[
    [AutocompleteErrorHandlerCallbackT[Any]],
    MetaStruct[AutocompleteErrorHandlerCallbackT[Any], Any],
]:
    return _catch_autocomplete(*exceptions)
