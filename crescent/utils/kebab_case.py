from __future__ import annotations

import re

__all__ = ("kebab_case",)


def kebab_case(name: str) -> str:
    """Convert an inferred command or option name to kebab-case."""

    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1-\2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name)
    return name.replace("_", "-").lower()
