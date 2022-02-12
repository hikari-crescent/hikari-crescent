from __future__ import annotations

from sys import version_info

from typing import get_type_hints, TYPE_CHECKING
from inspect import Parameter, signature

if TYPE_CHECKING:
    from typing import Any, Callable, Sequence

__all__: Sequence[str] = (
    "get_parameters",
)


def convert_signiture(param: Parameter, type_hints) -> Parameter:
    annotation = type_hints.get(param.name, None)
    return Parameter(
        name=param.name,
        annotation=annotation or param.annotation,
        default=param.default,
        kind=param.kind,
    )


def get_parameters(func: Callable[..., Any]) -> Sequence[Parameter]:
    if version_info >= (3, 10):
        # Mypy is on python version 3.8 but this is only valid in 3.10+
        return signature(func, eval_str=True).parameters.values()  # type: ignore

    type_hints = get_type_hints(func)
    sig = signature(func)

    return [
        convert_signiture(param, type_hints) for param in sig.parameters.values()
    ]
