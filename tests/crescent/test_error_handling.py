import hikari

import crescent
from tests.utils import MockBot


class TestErrorHandling:
    def test_command_error_handling(self):
        bot = MockBot()

        class TestException(Exception):
            pass

        @bot.include
        @crescent.catch_command(TestException)
        async def command(exc: Exception, ctx: crescent.Context):
            ...

        assert bot._command_error_handler.registry.get(TestException) is command

    def test_event_error_handling(self):
        bot = MockBot()

        class TestException(Exception):
            pass

        @bot.include
        @crescent.catch_event(TestException)
        async def command(exc: Exception, event: hikari.Event):
            ...

        assert bot._event_error_handler.registry.get(TestException) is command

    def test_autocomplete_error_handling(self):
        bot = MockBot()

        class TestException(Exception):
            pass

        @bot.include
        @crescent.catch_autocomplete(TestException)
        async def command(
            exc: Exception, ctx: crescent.Context, option: hikari.AutocompleteInteractionOption
        ):
            ...

        assert bot._autocomplete_error_handler.registry.get(TestException) is command
