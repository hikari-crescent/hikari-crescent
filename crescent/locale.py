from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

__all__ = ("LocaleBuilder", "str_or_build_locale")


class LocaleBuilder(ABC):
    """
    A class that can be inherited from to created APIs to use locales in your
    code.
    """

    @abstractmethod
    def build(self) -> Mapping[str, str]:
        """
        Builds the locales for a command. Returns a `Mapping` of
        language codes to strings.

        [Discord API Docs Localization.](https://discord.com/developers/docs/interactions/application-commands#localization)
        """

    @property
    @abstractmethod
    def fallback(self) -> str:
        """Return the name used when there is no localization for a language."""


def str_or_build_locale(string_or_locale: str | LocaleBuilder) -> tuple[str, Mapping[str, str]]:
    if isinstance(string_or_locale, LocaleBuilder):
        return (string_or_locale.fallback, string_or_locale.build())
    return (string_or_locale, {})
