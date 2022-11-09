import crescent
from crescent.locale import str_or_build_locale


class TestBuilder(crescent.LocaleBuilder):
    def build(self):
        return "LOCALES"

    def default(self):
        return "DEFAULT"


def test_str_or_build_locale():
    default, locales = str_or_build_locale(TestBuilder())

    assert default == "DEFAULT"
    assert locales == "LOCALES"

    default, locales = str_or_build_locale("test")

    assert default == "test"
    assert not locales
