from typing import Sequence, Any
from inspect import isclass


__all__: Sequence[str] = ("any_issubclass",)


def any_issubclass(obj: Any, cls: type) -> bool:
    if not isclass(obj):
        return False
    return issubclass(obj, cls)
