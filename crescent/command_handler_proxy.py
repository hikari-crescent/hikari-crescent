from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from crescent.internal.registry import CommandHandler
    from crescent.internal.app_command import AppCommandMeta, AppCommand


class CommandHandlerProxy:
    """
    Proxy for `crescent.internal.registry.CommandHandler` that allows users to use
    specific functions. This allows the implemtation of `crescent.internal.registry.CommandHandler`
    to be changed without it being a breaking change.
    """

    def __init__(self, command_handler: CommandHandler) -> None:
        self._command_handler = command_handler

    async def register_commands(self) -> None:
        await self._command_handler.register_commands()

    @property
    def crescent_commands(self) -> Iterable[AppCommandMeta]:
        """
        Returns the information crescent stores for all the commands registered
        to the bot.
        """
        return (
            command.metadata for command in
            self._command_handler.registry.values()
        )

    @property
    def app_commands(self) -> Iterable[AppCommand]:
        """
        Returns the app commands registered to this bot.
        """
        return (
            command.metadata.app_command for command in
            self._command_handler.registry.values()
        )
