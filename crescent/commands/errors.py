from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Generic, Protocol, Type, TypeVar

from attrs import define

from crescent.internal.meta_struct import MetaStruct

if TYPE_CHECKING:
    from crescent.context import Context
    from crescent.internal.app_command import AppCommandMeta, CommandCallback
    from crescent.typedefs import CommandOptionsT


ERROR = TypeVar("ERROR", bound=Exception, contravariant=True)


class ErrorHandlerProto(Protocol, Generic[ERROR]):
    async def __call__(
        self,
        /,
        *,
        exc: ERROR,
        ctx: Context,
        command: MetaStruct[CommandCallback, AppCommandMeta],
        options: CommandOptionsT,
    ) -> None:
        ...


@define
class ErrorHandlerMeta:
    pass


def catch(
    exception: Type[ERROR],
) -> Callable[
    [ErrorHandlerProto[ERROR] | MetaStruct[ErrorHandlerProto[ERROR], ErrorHandlerMeta]],
    MetaStruct[ErrorHandlerProto[ERROR], ErrorHandlerMeta],
]:
    def decorator(
        callback: ErrorHandlerProto[ERROR] | MetaStruct[ErrorHandlerProto[ERROR], ErrorHandlerMeta]
    ) -> MetaStruct[ErrorHandlerProto[ERROR], ErrorHandlerMeta]:
        if isinstance(callback, MetaStruct):
            meta = callback
        else:
            meta = MetaStruct(
                callback,
                ErrorHandlerMeta(),
            )

        def app_set_hook(meta: MetaStruct[ErrorHandlerProto[ERROR], ErrorHandlerMeta]) -> None:
            meta.app._error_handler.registry.setdefault(exception, []).append(meta)

        meta.app_set_hooks.append(app_set_hook)
        return meta

    return decorator
