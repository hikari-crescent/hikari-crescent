from __future__ import annotations

from crescent import LocaleBuilder
from dataclasses import dataclass
from typing import Sequence

try:
    import i18n as i18n_  # pyright: ignore
except ImportError:
    i18n_ = None


__all__: Sequence[str] = ("i18n", "LocaleString")


def _translate(key: str, *, locale: str | None = None) -> str:
    return i18n_.t(key, locale=locale)  # type: ignore


class i18n(LocaleBuilder):
    def __init__(self, key: str) -> None:
        if not i18n_:
            raise ModuleNotFoundError("`python-i18n` must be installed to use i18n.")

        self.key = key
        self.translations: dict[str, str] = {
            "da": _translate(self.key, locale="da"),
            "de": _translate(self.key, locale="de"),
            "en-GB": _translate(self.key, locale="en-GB"),
            "en-US": _translate(self.key, locale="en-US"),
            "es-ES": _translate(self.key, locale="en-ES"),
            "fr": _translate(self.key, locale="fr"),
            "hr": _translate(self.key, locale="hr"),
            "it": _translate(self.key, locale="it"),
            "lt": _translate(self.key, locale="lt"),
            "hu": _translate(self.key, locale="hu"),
            "nl": _translate(self.key, locale="nl"),
            "no": _translate(self.key, locale="no"),
            "pl": _translate(self.key, locale="pl"),
            "pt-BR": _translate(self.key, locale="pt-BR"),
            "ro": _translate(self.key, locale="ro"),
            "fi": _translate(self.key, locale="fi"),
            "sv-SE": _translate(self.key, locale="sv-SE"),
            "vi": _translate(self.key, locale="vi"),
            "tr": _translate(self.key, locale="tr"),
            "cs": _translate(self.key, locale="cs"),
            "el": _translate(self.key, locale="el"),
            "bg": _translate(self.key, locale="bg"),
            "ru": _translate(self.key, locale="ru"),
            "uk": _translate(self.key, locale="uk"),
            "hi": _translate(self.key, locale="hi"),
            "th": _translate(self.key, locale="th"),
            "zh-CN": _translate(self.key, locale="zh-CN"),
            "ja": _translate(self.key, locale="ja"),
            "zh-TW": _translate(self.key, locale="zh-TW"),
            "ko": _translate(self.key, locale="ko"),
        }

    def build(self) -> dict[str, str]:
        return self.translations

    def default(self) -> str:
        return self.key


@dataclass
class LocaleString(LocaleBuilder):
    fallback: str
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

    def default(self) -> str:
        return self.fallback
