from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, Awaitable, cast

from sigparse import Signature, sigparse

from crescent.context.base_context import BaseContext
from crescent.context.context import Context
from crescent.utils import any_issubclass

if TYPE_CHECKING:
    from typing import Any, Callable, Sequence, TypeVar

    from typing_extensions import ParamSpec

    T = TypeVar("T")
    P = ParamSpec("P")


__all__: Sequence[str] = ("support_custom_context", "get_function_context", "get_context_type")


def _get_ctx(args: Sequence[Any]) -> tuple[BaseContext, int]:
    """Get a variable of type `BaseContext` from a list."""
    for index, arg in enumerate(args):
        if isinstance(arg, BaseContext):
            return arg, index
    raise ValueError("Args do not include a `BaseContext` object.")


def support_custom_context(
    func: Callable[P, Awaitable[T]]
) -> Callable[P, Awaitable[tuple[T, BaseContext]]]:
    """
    Returns a function that is called with the context type it is annotated with.
    """

    ctx_t = get_function_context(func)

    @wraps(func)
    async def inner(*args: P.args, **kwargs: P.kwargs) -> tuple[T, BaseContext]:
        ctx, index = _get_ctx(args)

        argv: Sequence[Any]
        if type(ctx) is not ctx_t:
            ctx = ctx.into(ctx_t)
            argv = list(args)
            argv[index] = ctx
        else:
            argv = args

        return await func(*argv, **kwargs), ctx  # pyright: ignore

    return inner


def get_function_context(func: Callable[..., Any]) -> type[BaseContext]:
    """
    Gets the context type used in a function.
    """
    return get_context_type(sigparse(func)) or Context


def get_context_type(sig: Signature) -> type[BaseContext] | None:
    """
    Returns the Context type the function uses or `None` if the function is not annotated with
    a subclass of `BaseContext`
    """
    for param in sig.parameters:
        if any_issubclass(param.annotation, BaseContext):
            return cast("type[BaseContext]", param.annotation)
    return None
