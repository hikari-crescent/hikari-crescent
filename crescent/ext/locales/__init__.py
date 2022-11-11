from __future__ import annotations

from crescent import LocaleBuilder
from dataclasses import dataclass
from typing import Sequence

try:
    import i18n as i18n_  # pyright: ignore
except ImportError:
    i18n_ = None


__all__: Sequence[str] = ("i18n", "LocaleMap")


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
            "da": _translate(self.fallback, locale="da"),
            "de": _translate(self.fallback, locale="de"),
            "en-GB": _translate(self.fallback, locale="en-GB"),
            "en-US": _translate(self.fallback, locale="en-US"),
            "es-ES": _translate(self.fallback, locale="es-ES"),
            "fr": _translate(self.fallback, locale="fr"),
            "hr": _translate(self.fallback, locale="hr"),
            "it": _translate(self.fallback, locale="it"),
            "lt": _translate(self.fallback, locale="lt"),
            "hu": _translate(self.fallback, locale="hu"),
            "nl": _translate(self.fallback, locale="nl"),
            "no": _translate(self.fallback, locale="no"),
            "pl": _translate(self.fallback, locale="pl"),
            "pt-BR": _translate(self.fallback, locale="pt-BR"),
            "ro": _translate(self.fallback, locale="ro"),
            "fi": _translate(self.fallback, locale="fi"),
            "sv-SE": _translate(self.fallback, locale="sv-SE"),
            "vi": _translate(self.fallback, locale="vi"),
            "tr": _translate(self.fallback, locale="tr"),
            "cs": _translate(self.fallback, locale="cs"),
            "el": _translate(self.fallback, locale="el"),
            "bg": _translate(self.fallback, locale="bg"),
            "ru": _translate(self.fallback, locale="ru"),
            "uk": _translate(self.fallback, locale="uk"),
            "hi": _translate(self.fallback, locale="hi"),
            "th": _translate(self.fallback, locale="th"),
            "zh-CN": _translate(self.fallback, locale="zh-CN"),
            "ja": _translate(self.fallback, locale="ja"),
            "zh-TW": _translate(self.fallback, locale="zh-TW"),
            "ko": _translate(self.fallback, locale="ko"),
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
        locales = {
            "da": self.da,
            "de": self.de,
            "en-GB": self.en_GB,
            "en-US": self.en_US,
            "es-ES": self.es_ES,
            "fr": self.fr,
            "hr": self.hr,
            "it": self.it,
            "lt": self.lt,
            "hu": self.hu,
            "nl": self.nl,
            "no": self.no,
            "pl": self.pl,
            "pt-BR": self.pt_BR,
            "ro": self.ro,
            "fi": self.fi,
            "sv-SE": self.sv_SE,
            "vi": self.vi,
            "tr": self.tr,
            "cs": self.cs,
            "el": self.el,
            "bg": self.bg,
            "ru": self.ru,
            "uk": self.uk,
            "hi": self.hi,
            "th": self.th,
            "zh-CN": self.zh_CN,
            "ja": self.ja,
            "zh-TW": self.zh_TW,
            "ko": self.ko,
        }

        return {k: v for k, v in locales.items() if v}

    @property
    def fallback(self) -> str:
        return self._fallback
