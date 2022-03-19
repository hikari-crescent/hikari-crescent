from __future__ import annotations

from tests.crescent.plugins.plugin import plugin as real_plugin
from tests.utils import MockBot


def test_load_plugin():
    bot = MockBot()

    plugin = bot.plugins.load("tests.crescent.plugins.plugin")

    assert plugin is real_plugin


def test_plugin_reload():
    bot = MockBot()

    orig = bot.plugins.load("tests.crescent.plugins.plugin")
    del bot.plugins.plugins[real_plugin.name]
    orig2 = bot.plugins.load("tests.crescent.plugins.plugin")
    new = bot.plugins.load("tests.crescent.plugins.plugin", refresh=True)

    assert orig is orig2
    assert orig is not new
