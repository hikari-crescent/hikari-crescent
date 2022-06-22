from __future__ import annotations

from inspect import Parameter, signature
from sys import version_info
from typing import TYPE_CHECKING, get_type_hints

if TYPE_CHECKING:
    from typing import Any, Callable, Sequence

__all__: Sequence[str] = ("get_parameters",)


def convert_signiture(param: Parameter, type_hints: dict[str, type[Any]]) -> Parameter:
    annotation = type_hints.get(param.name)
    return Parameter(
        name=param.name,
        annotation=annotation or param.annotation,
        default=param.default,
        kind=param.kind,
    )


def get_parameters(func: Callable[..., Any]) -> Sequence[Parameter]:
    # NOTE: type: ignore is used because mypy and pyright are on python version 3.8

    if version_info >= (3, 10):
        return signature(func, eval_str=True).parameters.values()  # type: ignore

    if version_info >= (3, 9):
        type_hints: dict[str, Any] = get_type_hints(func, include_extras=True)  # type: ignore
    else:
        type_hints = get_type_hints(func)

    sig = signature(func)

    return [convert_signiture(param, type_hints) for param in sig.parameters.values()]
