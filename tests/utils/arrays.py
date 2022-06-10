from __future__ import annotations

from typing import Any, Sequence

__all__: Sequence[str] = ("arrays_contain_same_elements",)


def arrays_contain_same_elements(arr1: list[Any], arr2: list[Any]) -> bool:
    return set(arr1) == set(arr2)
