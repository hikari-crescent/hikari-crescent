from dataclasses import dataclass
from functools import wraps
from sys import version_info
from typing import Any

__all__ = ("fast_dataclass",)


@wraps(dataclass)
def fast_dataclass(*args: Any, **kwargs: Any) -> Any:
    if version_info < (3, 10):
        return dataclass(*args, **kwargs)

    if version_info < (3, 11):
        return dataclass(*args, **kwargs, slots=True)  # type: ignore

    return dataclass(*args, **kwargs, slots=True, weakref_slot=False)  # type: ignore
