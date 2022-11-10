from __future__ import annotations

from crescent import LocaleBuilder
from dataclasses import dataclass

try:
    import i18n as i18n_  # pyright: ignore
except ImportError:
    i18n_ = None


def translate(key: str, *, locale: str | None = None) -> str:
    return i18n_.t(key, locale=locale)  # type: ignore


class i18n(LocaleBuilder):
    def __init__(self, key: str) -> None:
        if not i18n_:
            raise ModuleNotFoundError("`python-i18n` must be installed to use i18n.")

        self.key = key
        self.translations: dict[str, str] = {
            "da": translate(self.key, locale="da"),
            "de": translate(self.key, locale="de"),
            "en-GB": translate(self.key, locale="en-GB"),
            "en-US": translate(self.key, locale="en-US"),
            "es-ES": translate(self.key, locale="en-ES"),
            "fr": translate(self.key, locale="fr"),
            "hr": translate(self.key, locale="hr"),
            "it": translate(self.key, locale="it"),
            "lt": translate(self.key, locale="lt"),
            "hu": translate(self.key, locale="hu"),
            "nl": translate(self.key, locale="nl"),
            "no": translate(self.key, locale="no"),
            "pl": translate(self.key, locale="pl"),
            "pt-BR": translate(self.key, locale="pt-BR"),
            "ro": translate(self.key, locale="ro"),
            "fi": translate(self.key, locale="fi"),
            "sv-SE": translate(self.key, locale="sv-SE"),
            "vi": translate(self.key, locale="vi"),
            "tr": translate(self.key, locale="tr"),
            "cs": translate(self.key, locale="cs"),
            "el": translate(self.key, locale="el"),
            "bg": translate(self.key, locale="bg"),
            "ru": translate(self.key, locale="ru"),
            "uk": translate(self.key, locale="uk"),
            "hi": translate(self.key, locale="hi"),
            "th": translate(self.key, locale="th"),
            "zh-CN": translate(self.key, locale="zh-CN"),
            "ja": translate(self.key, locale="ja"),
            "zh-TW": translate(self.key, locale="zh-TW"),
            "ko": translate(self.key, locale="ko"),
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
