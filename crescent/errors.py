from __future__ import annotations

from typing import Any, Awaitable, Callable, Sequence, Type, TypeVar

from crescent.internal.meta_struct import MetaStruct
from crescent.typedefs import (
    CommandErrorHandlerCallbackT,
    EventErrorHandlerCallbackT,
    AutocompleteErrorHandlerCallbackT,
)


__all__: Sequence[str] = ("catch_command", "catch_event", "catch_autocomplete")


T = TypeVar("T", bound=Callable[..., Awaitable[Any]])


def _make_catch_function(
    error_handler_var: str,
) -> Callable[
    [Type[Exception]],
    Callable[
        [T | MetaStruct[T, Any]],
        MetaStruct[T, Any],
    ],
]:
    def func(
        *exceptions: Type[Exception],
    ) -> Callable[[T | MetaStruct[T, Any]], MetaStruct[T, Any]]:
        def decorator(callback: T | MetaStruct[T, Any]) -> MetaStruct[T, Any]:
            if isinstance(callback, MetaStruct):
                meta = callback
            else:
                meta = MetaStruct(callback, None)

            def app_set_hook(meta: MetaStruct[T, Any]) -> None:
                for exc in exceptions:
                    getattr(meta.app, error_handler_var).register(meta, exc)

            meta.app_set_hooks.append(app_set_hook)
            return meta

        return decorator

    return func


def catch_command(
    *exceptions: Type[Exception],
) -> Callable[
    [CommandErrorHandlerCallbackT[Any] | MetaStruct[CommandErrorHandlerCallbackT[Any], Any]],
    MetaStruct[CommandErrorHandlerCallbackT[Any], Any],
]:
    return _make_catch_function("_command_error_handler")(*exceptions)


def catch_event(
    *exceptions: Type[Exception],
) -> Callable[
    [EventErrorHandlerCallbackT[Any] | MetaStruct[EventErrorHandlerCallbackT[Any], Any]],
    MetaStruct[EventErrorHandlerCallbackT[Any], Any],
]:
    return _make_catch_function("_event_error_handler")(*exceptions)


def catch_autocomplete(
    *exceptions: Type[Exception],
) -> Callable[
    [
        AutocompleteErrorHandlerCallbackT[Any]
        | MetaStruct[AutocompleteErrorHandlerCallbackT[Any], Any]
    ],
    MetaStruct[AutocompleteErrorHandlerCallbackT[Any], Any],
]:
    return _make_catch_function("_autocomplete_error_handler")(*exceptions)
