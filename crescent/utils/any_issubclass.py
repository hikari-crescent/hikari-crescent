from inspect import isclass
from typing import Any, Sequence

__all__: Sequence[str] = ("any_issubclass",)


def any_issubclass(obj: Any, cls: type) -> bool:
    if not isclass(obj):
        return False
    return issubclass(obj, cls)
