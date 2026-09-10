from __future__ import annotations

from typing import cast

__all__ = ("get_name",)


def get_name(obj: object, *, fallback: str = "<unknown>", error: str | None = None) -> str:
    if n := getattr(obj, "__name__", None):
        return cast("str", n)

    if error:
        raise RuntimeError(error)
    return fallback
