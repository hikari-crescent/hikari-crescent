from asyncio import Event, Task

from hikari import GatewayBot, Snowflake, StartedEvent

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
        self._wait_until_ready_event = Event()

    async def _on_started(self, event: StartedEvent) -> Task:
        event = await super()._on_started(event)
        if event:
            await event
        self._wait_until_ready_event.set()
        return None

    async def wait_until_ready(self):
        await self._wait_until_ready_event.wait()

    def run(self):
        self._app.run()


class MockBot(GatewayBot):
    def __init__(self):
        super().__init__(token="")

    def run(self):
        self.dispatch(StartedEvent(app=self))
