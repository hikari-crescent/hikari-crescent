from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, Type, cast

from crescent.exceptions import AlreadyRegisteredError
from crescent.internal.meta_struct import MetaStruct

if TYPE_CHECKING:
    from crescent.context import Context
    from crescent.typedefs import ERROR, ErrorHandlerCallbackT


_InternalErrorHandlerCallbackT = Callable[["ERROR", "Context"], Awaitable[None]]


def catch(
    *exceptions: Type[Exception],
) -> Callable[
    [ErrorHandlerCallbackT | MetaStruct[_InternalErrorHandlerCallbackT, Any]],
    MetaStruct[_InternalErrorHandlerCallbackT, Any],
]:
    def decorator(
        callback: ErrorHandlerCallbackT | MetaStruct[_InternalErrorHandlerCallbackT, Any]
    ) -> MetaStruct[_InternalErrorHandlerCallbackT, Any]:
        if isinstance(callback, MetaStruct):
            meta = callback
        else:
            callback = cast(_InternalErrorHandlerCallbackT, callback)
            meta = MetaStruct(callback, None)

        def app_set_hook(meta: MetaStruct[_InternalErrorHandlerCallbackT, Any]) -> None:
            for exc in exceptions:
                registry = meta.app._error_handler.registry
                if reg_meta := registry.get(exc):
                    raise AlreadyRegisteredError(
                        f"`{getattr(callback, '__name__')}` can not catch `{exc.__name__}`."
                        f"`{exc.__name__}` is already registered to"
                        f" `{reg_meta.callback.__name__}`."
                    )

                registry[exc] = meta

        meta.app_set_hooks.append(app_set_hook)
        return meta

    return decorator
