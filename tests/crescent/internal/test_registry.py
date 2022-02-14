from unittest.mock import AsyncMock, MagicMock

from hikari.impl import CacheImpl, RESTClientImpl
from pytest import fixture, mark

from crescent import Context, command
from tests.utils import MockBot

GUILD_ID = 123456789


class TestRegistry:
    @fixture(autouse=True)
    def mock_send(self):
        self.posted_commands = {}

        def set_application_commands(application, commands, guild=None):
            self.posted_commands[guild] = commands

        RESTClientImpl.set_application_commands = AsyncMock(return_value=None)
        RESTClientImpl.set_application_commands.side_effect = set_application_commands

        CacheImpl.get_guilds_view = MagicMock(return_value={0: GUILD_ID})

    @mark.asyncio
    async def test_post_commands(self):
        bot = MockBot(default_guild=GUILD_ID)

        @bot.include
        @command
        async def command_one(ctx: Context):
            pass

        @bot.include
        @command
        async def command_two(ctx: Context):
            pass

        bot._command_handler.application_id = ...

        await bot._command_handler.register_commands()

        assert self.posted_commands[GUILD_ID] == [
            command_one.metadata.app,
            command_two.metadata.app,
        ]

    @mark.asyncio
    async def test_post_deprecated_commands(self):
        bot = MockBot(default_guild=GUILD_ID)

        @bot.include
        @command(deprecated=True)
        async def command_one(ctx: Context):
            pass

        @bot.include
        @command
        async def command_two(ctx: Context):
            pass

        await bot._command_handler.register_commands()

        assert self.posted_commands[GUILD_ID] == [command_two.metadata.app]
