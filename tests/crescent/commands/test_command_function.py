from typing import Optional

from hikari import UNDEFINED, CommandOption, CommandType, Message, OptionType, User
from typing_extensions import Annotated as Atd

from crescent import Context, command, message_command, user_command
from crescent.internal.app_command import AppCommand, AppCommandMeta


def test_command_function():
    @command(description="1234")
    async def callback(
        ctx: Context,
        arg_1: Atd[str, "1234"],
        arg_2: Atd[Optional[str], "1234"] = None,
        arg_3: Optional[float] = None,
    ):
        pass

    assert callback.metadata == AppCommandMeta(
        app=AppCommand(
            type=CommandType.SLASH,
            name="callback",
            guild_id=None,
            default_permission=UNDEFINED,
            description="1234",
            options=[
                CommandOption(
                    type=OptionType.STRING, name="arg_1", description="1234", is_required=True
                ),
                CommandOption(
                    type=OptionType.STRING, name="arg_2", description="1234", is_required=False
                ),
                CommandOption(
                    type=OptionType.FLOAT,
                    name="arg_3",
                    description="No Description",
                    is_required=False,
                ),
            ],
        )
    )

    @command(name="test", description="1234", guild=12345678)
    async def callback(ctx: Context):
        pass

    assert callback.metadata == AppCommandMeta(
        app=AppCommand(
            type=CommandType.SLASH,
            name="test",
            guild_id=12345678,
            default_permission=UNDEFINED,
            description="1234",
        )
    )

    @message_command
    async def callback(ctx: Context, message: Message):
        pass

    assert callback.metadata == AppCommandMeta(
        app=AppCommand(
            type=CommandType.MESSAGE, name="callback", default_permission=UNDEFINED, guild_id=None
        )
    )

    @user_command
    async def callback(ctx: Context, user: User):
        pass

    assert callback.metadata == AppCommandMeta(
        app=AppCommand(
            type=CommandType.USER, name="callback", default_permission=UNDEFINED, guild_id=None
        )
    )
