from __future__ import annotations

from dataclasses import dataclass

from hikari import Locale


@dataclass
class LocaleStr:
    default: str

    def to_dict(self) -> dict[Locale, str]:
        localized: dict[Locale, str] = {}
        for locale in Locale:
            locale_str = getattr(self, locale.name, None)
            if locale_str is None:
                continue
            localized[locale] = locale_str
        return localized

    DA: str | None = None
    """Danish"""
    DE: str | None = None
    """German"""
    EN_GB: str | None = None
    """English, UK"""
    EN_US: str | None = None
    """English, US"""
    ES_ES: str | None = None
    """Spanish"""
    FR: str | None = None
    """French"""
    HR: str | None = None
    """Croatian"""
    IT: str | None = None
    """Italian"""
    LT: str | None = None
    """Lithuanian"""
    HU: str | None = None
    """Hungarian"""
    NL: str | None = None
    """Dutch"""
    NO: str | None = None
    """Norwegian"""
    OL: str | None = None
    """Polish"""
    PT_BR: str | None = None
    """Portuguese, Bralizian"""
    RO: str | None = None
    """Romian"""
    FI: str | None = None
    """Finnish"""
    SV_SE: str | None = None
    """Swedish"""
    VI: str | None = None
    """Vietnamese"""
    TR: str | None = None
    """Turkish"""
    CS: str | None = None
    """Czech"""
    EL: str | None = None
    """Greek"""
    BG: str | None = None
    """Bulgarian"""
    RU: str | None = None
    """Russian"""
    UK: str | None = None
    """Ukrainian"""
    HI: str | None = None
    """Hindi"""
    TH: str | None = None
    """Thai"""
    ZH_CN: str | None = None
    """Chinese, China"""
    JA: str | None = None
    """Japanese"""
    ZH_TW: str | None = None
    """Chinese, Taiwan"""
    KO: str | None = None
    """Korean"""
