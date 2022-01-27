from __future__ import annotations
from inspect import iscoroutinefunction

from typing import TYPE_CHECKING, Sequence
from functools import partial

from attrs import define

from crescent.internal.meta_struct import MetaStruct


if TYPE_CHECKING:
    from typing import TypeVar, Any, Awaitable, Callable
    from typing_extensions import ParamSpec, Concatenate
    from crescent.context import Context

    P = ParamSpec("P")
    T = TypeVar("T", bound="MetaStruct[Callable[..., Awaitable[Any]], Any]")

__all__: Sequence[str] = (
    "HookResult",
    "interaction_hook",
)


@define
class HookResult:
    pass


class _PartialFunction:
    """Works similarly to functools.partial but added arguments are prepended instead
    of appended.
    """

    def __init__(self, func, *args, **kwargs) -> None:
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, *self.args, **kwargs, **self.kwargs)


# This function is compatible with pep 612 (https://www.python.org/dev/peps/pep-0612/)
# but mypy doesn't understand it.
def interaction_hook(
    callback: Callable[Concatenate[Context, P], Awaitable[HookResult]]  # type: ignore
) -> Callable[P, T]:
    if not iscoroutinefunction(callback):
        raise ValueError(f"Function `{callback.__name__}` must be async.")

    def decorator(*args: Any, **kwargs: Any):
        if not args or (args and not isinstance(args[-1], MetaStruct)):
            return partial(decorator, *args, **kwargs)

        command = args[-1]
        args = args[:-1]

        command.extensions.append(_PartialFunction(callback, *args, **kwargs))
        return command

    return decorator
