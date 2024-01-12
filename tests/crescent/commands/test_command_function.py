from types import FunctionType
from typing import Optional

from hikari import (
    UNDEFINED,
    ChannelType,
    CommandOption,
    CommandType,
    Message,
    OptionType,
    PartialChannel,
    User,
)
from typing_extensions import Annotated

from crescent import Context, command, message_command, user_command
from crescent.internal.app_command import AppCommand, AppCommandMeta


class TestCommandFunction:
    def test_slash_command(self):
        @command(name="test", description="1234", guild=12345678)
        async def callback(ctx: Context):
            pass

        assert isinstance(callback.metadata.owner, FunctionType)

        assert callback.metadata == AppCommandMeta(
            owner=callback.metadata.owner,
            callback=callback.metadata.callback,
            app_command=AppCommand(
                type=CommandType.SLASH,
                name="test",
                guild_id=12345678,
                default_member_permissions=UNDEFINED,
                is_dm_enabled=True,
                description="1234",
            ),
        )

    def test_message_command(self):
        @message_command
        async def callback(ctx: Context, message: Message):
            pass

        assert callback.metadata == AppCommandMeta(
            owner=callback.metadata.owner,
            callback=callback.metadata.callback,
            app_command=AppCommand(
                type=CommandType.MESSAGE,
                name="callback",
                default_member_permissions=UNDEFINED,
                is_dm_enabled=True,
                guild_id=None,
            ),
        )

    def test_user_command(self):
        @user_command
        async def callback(ctx: Context, user: User):
            pass

        assert isinstance(callback.metadata.owner, FunctionType)

        assert callback.metadata == AppCommandMeta(
            owner=callback.metadata.owner,
            callback=callback.metadata.callback,
            app_command=AppCommand(
                type=CommandType.USER,
                name="callback",
                default_member_permissions=UNDEFINED,
                is_dm_enabled=True,
                guild_id=None,
            ),
        )
