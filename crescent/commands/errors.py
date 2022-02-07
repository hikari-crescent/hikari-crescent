from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Generic, Protocol, Type, TypeVar, overload

from crescent.internal.meta_struct import MetaStruct
from crescent.exceptions import AlreadyRegisteredError

if TYPE_CHECKING:
    from crescent.context import Context


ERROR = TypeVar("ERROR", bound=Exception, contravariant=True)


class ErrorHandlerProto(Protocol, Generic[ERROR]):
    __name__: str

    async def __call__(self, /, *, exc: ERROR, ctx: Context) -> None:
        ...


@overload
def catch(
    exception: Type[ERROR], /
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
            meta = MetaStruct(callback, None)

        def app_set_hook(meta: MetaStruct[ErrorHandlerProto[ERROR], Any]) -> None:
            for exc in exceptions:
                registry = meta.app._error_handler.registry
                if reg_meta := registry.get(exc):
                    raise AlreadyRegisteredError(
                        f"`{callback.__name__}` can not catch `{exc.__name__}`."
                        f"`{exc.__name__}` is already registered to"
                        f" `{reg_meta.callback.__name__}`."
                    )

                registry[exc] = meta

        meta.app_set_hooks.append(app_set_hook)
        return meta

    return decorator
