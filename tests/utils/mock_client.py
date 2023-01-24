from hikari import GatewayBot, Snowflake, StartedEvent, RESTBot

from crescent import Client
from crescent.internal.registry import CommandHandler


class MockClient(Client):
    def __init__(
        self, default_guild=None, update_commands=True, command_hooks=[], command_after_hooks=[]
    ) -> None:

        super().__init__(
            app=MockBot(),
            update_commands=update_commands,
            command_hooks=command_hooks,
            command_after_hooks=command_after_hooks,
        )

        self.default_guild = default_guild

        self._command_handler = CommandHandler(self, [])
        self._command_handler._application_id = Snowflake()


class MockRESTClient(Client):
    def __init__(
        self, default_guild=None, update_commands=True, command_hooks=[], command_after_hooks=[]
    ) -> None:

        super().__init__(
            app=RESTBot(token=None),
            update_commands=update_commands,
            command_hooks=command_hooks,
            command_after_hooks=command_after_hooks,
        )

        self.default_guild = default_guild

        self._command_handler = CommandHandler(self, [])
        self._command_handler._application_id = Snowflake()


class MockBot(GatewayBot):
    def __init__(self):
        super().__init__(token="")

    def run(self):
        self.dispatch(StartedEvent(app=self))
