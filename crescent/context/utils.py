from __future__ import annotations
from functools import lru_cache

from typing import TYPE_CHECKING, Awaitable, cast

from crescent.context.context import Context
from crescent.context.base_context import BaseContext

if TYPE_CHECKING:
    from typing import Callable, Any, Sequence, TypeVar

    from inspect import Parameter

    T = TypeVar("T")

from crescent.utils import get_parameters

__all__: Sequence[str] = ("call_with_context", "get_function_context", "get_context_type")


async def call_with_context(
    func: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any
) -> tuple[T, BaseContext]:
    """
    Calls a function with the context type it is annotated with.
    """

    ctx_t = get_function_context(func)

    ctx, index = get_ctx(args)
    new_ctx = ctx.into(ctx_t or Context)

    args_list = list(args)
    args_list[index] = new_ctx

    result = await func(*args_list, **kwargs)
    return result, new_ctx

def get_ctx(args: Sequence[Any]) -> tuple[BaseContext, int]:
    for index, arg in enumerate(args):
        if isinstance(arg, BaseContext):
            return arg, index
    raise ValueError("Args do not include a `BaseContext` object.")

@lru_cache
def get_function_context(func: Callable[..., Any]) -> type[BaseContext] | None:
    return get_context_type(get_parameters(func))


def get_context_type(params: Sequence[Parameter]) -> type[BaseContext] | None:
    """Returns the Context or `None` if there is no ctx"""
    for param in params:
        if issubclass(param.annotation, BaseContext):
            return cast("type[BaseContext]", param.annotation)
    return None
