from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from crescent import LocaleBuilder

__all__: Sequence[str] = ("Locale",)


@dataclass
class Locale(LocaleBuilder):

    default_name: str
    en_US: str | None = None

    def build(self) -> dict[str, str]:
        out: dict[str, str] = {}
        if self.en_US:
            out["en-US"] = self.en_US

        return out

    def default(self) -> str:
        return self.default_name
