from collections import defaultdict
from contextlib import ExitStack
from unittest.mock import AsyncMock, MagicMock, patch

from hikari import Message, User
from hikari.impl import CacheImpl, RESTClientImpl
from pytest import fixture, mark

from crescent import Context, command
from crescent import message_command as _message_command
from crescent import user_command as _user_command
from crescent.internal.registry import CommandHandler
from tests.utils import MockBot

GUILD_ID = 123456789


class TestRegistry:
    @fixture(autouse=True)
    def mock_send(self):
        self.posted_commands = defaultdict(list)

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
        async def user_command(ctx: Context, user: User):
            pass

        @bot.include
        @_message_command
        async def message_command(ctx: Context, message: Message):
            pass

        bot.run()
        await bot.wait_until_ready()

        assert self.posted_commands[GUILD_ID] == [
            slash_command.metadata.app,
            user_command.metadata.app,
            message_command.metadata.app,
        ]

    @mark.asyncio
    async def test_dont_register_commands(self):
        stack = ExitStack()
        register_commands = stack.enter_context(patch.object(CommandHandler, "register_commands"))

        bot = MockBot(default_guild=GUILD_ID, update_commands=False)

        @bot.include
        @command
        async def slash_command(ctx: Context):
            pass

        @bot.include
        @_user_command
        async def user_command(ctx: Context, user: User):
            pass

        @bot.include
        @_message_command
        async def message_command(ctx: Context, message: Message):
            pass

        bot.run()
        await bot.wait_until_ready()

        register_commands.assert_not_called()
        assert self.posted_commands[GUILD_ID] == []
