from crescent.locale import str_or_build_locale
from tests.utils import Locale


def test_str_or_build_locale():
    default, locales = str_or_build_locale(Locale("default", en_US="en-localization"))

    assert default == "default"
    assert locales == {"en-US": "en-localization"}

    default, locales = str_or_build_locale("test")

    assert default == "test"
    assert not locales
