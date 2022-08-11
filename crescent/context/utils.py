from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Awaitable, cast

from crescent.context.base_context import BaseContext
from crescent.context.context import Context

if TYPE_CHECKING:
    from inspect import Parameter
    from typing import Any, Callable, Sequence, TypeVar

    T = TypeVar("T")

from crescent.utils import get_parameters

__all__: Sequence[str] = ("call_with_context", "get_function_context", "get_context_type")


def _get_ctx(args: Sequence[Any]) -> tuple[BaseContext, int]:
    """Get a variable of type `BaseContext` from a list."""
    for index, arg in enumerate(args):
        if isinstance(arg, BaseContext):
            return arg, index
    raise ValueError("Args do not include a `BaseContext` object.")


async def call_with_context(
    func: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any
) -> tuple[T, BaseContext]:
    """
    Calls a function with the context type it is annotated with.
    """

    ctx_t = get_function_context(func) or Context

    ctx, index = _get_ctx(args)

    argv: Sequence[Any]
    if not isinstance(ctx, ctx_t):
        ctx = ctx.into(ctx_t)
        argv = list(args)
        argv[index] = ctx
    else:
        argv = args

    result = await func(*argv, **kwargs)
    return result, ctx


@lru_cache
def get_function_context(func: Callable[..., Any]) -> type[BaseContext] | None:
    """
    Gets the context type used in a function. Returns `None` if no parameters are
    annotated with a context.
    """
    return get_context_type(get_parameters(func))


def get_context_type(params: Sequence[Parameter]) -> type[BaseContext] | None:
    """Returns the Context or `None` if there is no ctx"""
    for param in params:
        if issubclass(param.annotation, BaseContext):
            return cast("type[BaseContext]", param.annotation)
    return None
