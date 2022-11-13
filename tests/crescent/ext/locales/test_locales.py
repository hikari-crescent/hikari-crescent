import hikari
from crescent.ext import locales


def test_contains_all_hikari_locales():
    for locale in locales.locales:
        hikari.Locale(locale)
