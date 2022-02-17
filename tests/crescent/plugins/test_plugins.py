from tests.utils import MockBot


class TestPlugins:
    def test_load_plugin(self):
        bot = MockBot()

        bot.plugins.load("plugin")
