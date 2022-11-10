from __future__ import annotations

from abc import ABC, abstractmethod
from typing import MutableMapping, Sequence

__all__: Sequence[str] = ("LocaleBuilder", "str_or_build_locale")


class LocaleBuilder(ABC):
    @abstractmethod
    def build(self) -> MutableMapping[str, str]:
        """
        Builds the locales for a command. Returns a `MutableMapping` of
        language codes to strings.

        [Discord API Docs Localization.](https://discord.com/developers/docs/interactions/application-commands#localization)
        """

    @property
    @abstractmethod
    def fallback(self) -> str:
        """Return the name used when there is no localization for a language."""


def str_or_build_locale(
    string_or_locale: str | LocaleBuilder,
) -> tuple[str, MutableMapping[str, str]]:
    if isinstance(string_or_locale, LocaleBuilder):
        return (string_or_locale.fallback, string_or_locale.build())
    else:
        return (string_or_locale, {})
