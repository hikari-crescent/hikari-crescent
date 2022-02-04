from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Protocol,
    Type,
    TypeVar,
    overload,
)

from crescent.internal.meta_struct import MetaStruct

if TYPE_CHECKING:
    from crescent.context import Context


ERROR = TypeVar("ERROR", bound=Exception, contravariant=True)


class ErrorHandlerProto(Protocol, Generic[ERROR]):
    async def __call__(
        self,
        /,
        *,
        exc: ERROR,
        ctx: Context,
    ) -> None:
        ...


@overload
def catch(
    exception: Type[ERROR],
    /,
) -> Callable[
    [ErrorHandlerProto[ERROR] | MetaStruct[ErrorHandlerProto[ERROR], Any]],
    MetaStruct[ErrorHandlerProto[ERROR], Any],
]:
    ...


@overload
def catch(
    *exceptions: Type[Exception],
) -> Callable[
    [ErrorHandlerProto[Any] | MetaStruct[ErrorHandlerProto[Any], Any]],
    MetaStruct[ErrorHandlerProto[Any], Any],
]:
    ...


def catch(
    *exceptions: Type[Exception],
) -> Callable[
    [ErrorHandlerProto[Any] | MetaStruct[ErrorHandlerProto[Any], Any]],
    MetaStruct[ErrorHandlerProto[Any], Any],
]:
    def decorator(
        callback: ErrorHandlerProto[ERROR] | MetaStruct[ErrorHandlerProto[ERROR], Any]
    ) -> MetaStruct[ErrorHandlerProto[ERROR], Any]:
        if isinstance(callback, MetaStruct):
            meta = callback
        else:
            meta = MetaStruct(
                callback,
                None,
            )

        def app_set_hook(meta: MetaStruct[ErrorHandlerProto[ERROR], Any]) -> None:
            for exc in exceptions:
                meta.app._error_handler.registry.setdefault(exc, []).append(meta)

        meta.app_set_hooks.append(app_set_hook)
        return meta

    return decorator
