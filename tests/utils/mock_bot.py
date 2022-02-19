from asyncio import Event, Task

from hikari import Snowflake, StartedEvent

from crescent import Bot
from crescent.internal.registry import CommandHandler


class MockBot(Bot):
    def __init__(self, default_guild=None, update_commands=True) -> None:

        super().__init__(token="", update_commands=update_commands)

        self.default_guild = default_guild

        self._command_handler = CommandHandler(self, [])
        self._command_handler.application_id = Snowflake()
        self._wait_until_ready_event = Event()

    async def _on_started(self, event: StartedEvent) -> Task:
        event = await super()._on_started(event)
        if event:
            await event
        self._wait_until_ready_event.set()
        return None

    def run(self):
        self.dispatch(StartedEvent(app=self))

    async def wait_until_ready(self):
        await self._wait_until_ready_event.wait()
