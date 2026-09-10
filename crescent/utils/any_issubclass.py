from __future__ import annotations

from inspect import isclass
from typing import Any

__all__ = ("any_issubclass",)


def any_issubclass(obj: Any, cls: type) -> bool:
    if not isclass(obj):
        return False
    return issubclass(obj, cls)
