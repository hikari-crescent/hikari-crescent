from unittest.mock import AsyncMock, MagicMock

from hikari.impl import CacheImpl, RESTClientImpl
from pytest import fixture, mark

from crescent import Context, command
from crescent import message_command as _message_command
from crescent import user_command as _user_command
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
        async def slash_command(ctx: Context):
            pass

        @bot.include
        @_user_command
        async def user_command(ctx: Context):
            pass

        @bot.include
        @_message_command
        async def message_command(ctx: Context):
            pass

        bot._command_handler.application_id = ...

        await bot._command_handler.register_commands()

        assert self.posted_commands[GUILD_ID] == [
            slash_command.metadata.app,
            user_command.metadata.app,
            message_command.metadata.app,
        ]

    @mark.asyncio
    async def test_post_deprecated_commands(self):
        bot = MockBot(default_guild=GUILD_ID)

        @bot.include
        @command(deprecated=True)
        async def slash_command_deprecated(ctx: Context):
            pass

        @bot.include
        @_user_command(deprecated=True)
        async def user_command_deprecated(ctx: Context):
            pass

        @bot.include
        @_message_command(deprecated=True)
        async def message_command_deprecated(ctx: Context):
            pass

        @bot.include
        @command
        async def slash_command(ctx: Context):
            pass

        @bot.include
        @_user_command
        async def user_command(ctx: Context):
            pass

        @bot.include
        @_message_command
        async def message_command(ctx: Context):
            pass

        await bot._command_handler.register_commands()

        assert self.posted_commands[GUILD_ID] == [
            slash_command.metadata.app,
            user_command.metadata.app,
            message_command.metadata.app,
        ]
