from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from crescent import LocaleBuilder

__all__: Sequence[str] = ("Locale",)


@dataclass
class Locale(LocaleBuilder):

    _fallback: str
    en_US: str | None = None

    def build(self) -> dict[str, str]:
        out: dict[str, str] = {}
        if self.en_US:
            out["en-US"] = self.en_US

        return out

    @property
    def fallback(self) -> str:
        return self._fallback
