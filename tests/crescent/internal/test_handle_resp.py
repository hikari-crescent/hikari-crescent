from pytest import mark

from hikari import CommandInteraction, CommandType, InteractionCreateEvent, InteractionType
from tests.utils import MockBot

from crescent import command, Context
from crescent.internal.handle_resp import handle_resp


@mark.asyncio
async def test_handle_resp():
    bot = MockBot()

    command_was_run = False

    @bot.include
    @command
    async def test_command(ctx: Context):
        nonlocal command_was_run
        command_was_run = True

    event = InteractionCreateEvent(
        shard=None,
        interaction=CommandInteraction(
            app=bot,
            id=None,
            application_id=bot.application_id,
            type=InteractionType.APPLICATION_COMMAND,
            token=bot.token,
            version=0,
            channel_id=0,
            guild_id=None,
            guild_locale=None,
            member=None,
            user=None,
            locale=None,
            command_id=None,
            command_name="test_command",
            command_type=CommandType.SLASH,
            resolved=None,
            options=None,
        ),
    )

    await handle_resp(event)

    assert command_was_run
