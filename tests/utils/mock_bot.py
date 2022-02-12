from crescent import Bot
from crescent.internal.registry import CommandHandler


class MockBot(Bot):
    def __init__(self) -> None:

        self.default_guild = None

        self.token = ""
        self.application_id = ""

        self._command_handler = CommandHandler(self, [])

    def run():
        raise Exception("`run` method of `MockBot` should never be used")
