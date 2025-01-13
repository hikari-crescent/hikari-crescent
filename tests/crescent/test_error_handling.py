import hikari

import crescent
from tests.utils import MockClient


class TestErrorHandling:
    def test_command_error_handling(self):
        client = MockClient()

        class TestException(Exception):
            pass

        @client.include
        @crescent.catch_command(TestException)
        async def command(exc: Exception, ctx: crescent.Context): ...

        assert client._command_error_handler.registry.get(TestException) is command

    def test_event_error_handling(self):
        client = MockClient()

        class TestException(Exception):
            pass

        @client.include
        @crescent.catch_event(TestException)
        async def command(exc: Exception, event: hikari.Event): ...

        assert client._event_error_handler.registry.get(TestException) is command

    def test_autocomplete_error_handling(self):
        client = MockClient()

        class TestException(Exception):
            pass

        @client.include
        @crescent.catch_autocomplete(TestException)
        async def command(
            exc: Exception, ctx: crescent.Context, option: hikari.AutocompleteInteractionOption
        ): ...

        assert client._autocomplete_error_handler.registry.get(TestException) is command
