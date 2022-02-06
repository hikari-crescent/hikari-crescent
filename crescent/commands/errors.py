from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, Type, cast, overload

from crescent.internal.meta_struct import MetaStruct

if TYPE_CHECKING:
    from crescent.typedefs import ERROR, ErrorHandlerCallbackT
    from crescent.context import Context


_ErrorHandlerCallback = Callable[["ERROR", "Context"], Awaitable[None]]


@overload
def catch(
    exception: Type[ERROR], /
) -> Callable[
    [ErrorHandlerCallbackT | MetaStruct[_ErrorHandlerCallback, Any]],
    MetaStruct[_ErrorHandlerCallback, Any],
]:
    ...


@overload
def catch(
    *exceptions: Type[Exception],
) -> Callable[
    [ErrorHandlerCallbackT | MetaStruct[_ErrorHandlerCallback, Any]],
    MetaStruct[_ErrorHandlerCallback, Any],
]:
    ...


def catch(
    *exceptions: Type[Exception],
) -> Callable[
    [ErrorHandlerCallbackT | MetaStruct[_ErrorHandlerCallback, Any]],
    MetaStruct[_ErrorHandlerCallback, Any],
]:
    def decorator(
        callback: ErrorHandlerCallbackT | MetaStruct[_ErrorHandlerCallback, Any]
    ) -> MetaStruct[_ErrorHandlerCallback, Any]:
        if isinstance(callback, MetaStruct):
            meta = callback
        else:
            callback = cast(_ErrorHandlerCallback, callback)
            meta = MetaStruct(callback, None)

        def app_set_hook(meta: MetaStruct[_ErrorHandlerCallback, Any]) -> None:
            for exc in exceptions:
                meta.app._error_handler.registry.setdefault(exc, []).append(meta)

        meta.app_set_hooks.append(app_set_hook)
        return meta

    return decorator
