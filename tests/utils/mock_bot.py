from hikari import Snowflake

from crescent import Bot
from crescent.internal.registry import CommandHandler


class MockBot(Bot):
    def __init__(self, default_guild=None, update_commands=True) -> None:

        super().__init__(token="", update_commands=update_commands)

        self.default_guild = default_guild

        self._command_handler = CommandHandler(self, [])
        self._command_handler.application_id = Snowflake()

    def run(self):
        raise Exception("`run` method of `MockBot` should never be used")
