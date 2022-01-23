from __future__ import annotations

from typing import Any, Iterator, Sequence
from itertools import chain

__all__: Sequence[str] = (
    "iterate_vars",
)


def iterate_vars(*objs) -> Iterator[Any]:
    return chain.from_iterable(
        chain(
            getattr(obj, "__dict__", {}).items(),
            {
                key: getattr(obj, key, None)
                for key in getattr(obj, "__slots__", [])
            }.items(),
        ) for obj in objs
    )
