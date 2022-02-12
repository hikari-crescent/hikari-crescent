from typing import Any

from crescent import Bot
from crescent.internal.meta_struct import MetaStruct
from crescent.internal.registry import CommandHandler


class MockBot(Bot):
    def __init__(self) -> None:

        self.default_guild = None

        self.token = ""
        self.application_id = ""

        self._command_handler = CommandHandler(self, [])

    def include(self, command: MetaStruct[Any, Any]):  # type: ignore
        self._command_handler.register(command)
        return command
