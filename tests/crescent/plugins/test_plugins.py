from __future__ import annotations

from tests.utils import MockBot
from tests.crescent.plugins.plugin import plugin as real_plugin


BOT = MockBot()


def test_load_plugin():
    plugin = BOT.plugins.load("tests.crescent.plugins.plugin")
    assert plugin is real_plugin
    del BOT.plugins.plugins[real_plugin.name]


def test_plugin_reload():
    orig = BOT.plugins.load("tests.crescent.plugins.plugin")
    del BOT.plugins.plugins[real_plugin.name]
    orig2 = BOT.plugins.load("tests.crescent.plugins.plugin")

    new = BOT.plugins.load("tests.crescent.plugins.plugin", refresh=True)

    assert orig is orig2
    assert orig is not new
