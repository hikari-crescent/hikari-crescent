from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from crescent import LocaleBuilder

try:
    import i18n as i18n_  # type: ignore
except ImportError:
    i18n_ = None


__all__: Sequence[str] = ("i18n", "LocaleMap", "locales")


locales = {
    "da",
    "de",
    "en-GB",
    "en-US",
    "es-ES",
    "fr",
    "hr",
    "it",
    "lt",
    "hu",
    "nl",
    "no",
    "pl",
    "pt-BR",
    "ro",
    "fi",
    "sv-SE",
    "vi",
    "tr",
    "cs",
    "el",
    "bg",
    "ru",
    "uk",
    "hi",
    "th",
    "zh-CN",
    "ja",
    "zh-TW",
    "ko",
}
"""A set of all possible locales."""


def _translate(key: str, *, locale: str | None = None) -> str:
    return i18n_.t(key, locale=locale)  # type: ignore


class i18n(LocaleBuilder):
    """
    An implementation of `crescent.LocaleBuilder` that uses `python-i18n`.

    > ⚠️ Translations must be loaded before any commands.

    ```python
    import crescent
    import i18n
    from crescent.ext import locales

    i18n.add_translation("name", "translated-name", locale="en")

    @bot.include
    @crescent.command(name=locales.i18n("name"))
    async def command(ctx: crescent.Context):
        ...
    ```
    """

    def __init__(self, fallback: str) -> None:
        if not i18n_:
            raise ModuleNotFoundError("`hikari-crescent[i18n]` must be installed to use i18n.")

        self._fallback = fallback
        self.translations: dict[str, str] = {
            locale: _translate(self._fallback, locale=locale) for locale in locales
        }

    def build(self) -> dict[str, str]:
        return self.translations

    @property
    def fallback(self) -> str:
        return self._fallback


@dataclass
class LocaleMap(LocaleBuilder):
    """
    An implementation of `crescent.LocaleBuilder` that allows you to declare locales as kwargs.

    ```python
    import crescent
    from crescent.ext import locales

    @bot.include
    @crescent.command(name=locales.LocaleMap("fallback", en_US="english-name", fr="french-name"))
    async def command(ctx: crescent.Context):
        ...
    ```
    """

    _fallback: str
    da: str | None = None
    de: str | None = None
    en_GB: str | None = None
    en_US: str | None = None
    es_ES: str | None = None
    fr: str | None = None
    hr: str | None = None
    it: str | None = None
    lt: str | None = None
    hu: str | None = None
    nl: str | None = None
    no: str | None = None
    pl: str | None = None
    pt_BR: str | None = None
    ro: str | None = None
    fi: str | None = None
    sv_SE: str | None = None
    vi: str | None = None
    tr: str | None = None
    cs: str | None = None
    el: str | None = None
    bg: str | None = None
    ru: str | None = None
    uk: str | None = None
    hi: str | None = None
    th: str | None = None
    zh_CN: str | None = None
    ja: str | None = None
    zh_TW: str | None = None
    ko: str | None = None

    def build(self) -> dict[str, str]:
        out: dict[str, str] = {}
        for locale in locales:
            value = getattr(self, locale.replace("-", "_"))
            if value:
                out[locale] = value

        return out

    @property
    def fallback(self) -> str:
        return self._fallback
