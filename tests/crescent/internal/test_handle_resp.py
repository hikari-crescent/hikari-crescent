from hikari import CommandInteraction, CommandType, InteractionCreateEvent, InteractionType
from pytest import mark

from crescent import Context, command, hook
from crescent.context.base_context import BaseContext
from crescent.internal.handle_resp import handle_resp
from tests.utils import MockBot


def MockEvent(name, bot):
    return InteractionCreateEvent(
        shard=None,
        interaction=CommandInteraction(
            app=bot,
            id=None,
            application_id=...,
            type=InteractionType.APPLICATION_COMMAND,
            token=bot._token,
            version=0,
            channel_id=0,
            guild_id=None,
            guild_locale=None,
            member=None,
            user=None,
            locale=None,
            command_id=None,
            command_name=name,
            command_type=CommandType.SLASH,
            resolved=None,
            options=None,
        ),
    )


@mark.asyncio
async def test_handle_resp_slash_function():
    bot = MockBot()

    command_was_run = False

    @bot.include
    @command
    async def test_command(ctx: Context):
        nonlocal command_was_run
        command_was_run = True
        assert type(ctx) is test_command.metadata.custom_context

    await handle_resp(MockEvent("test_command", bot))

    assert command_was_run


@mark.asyncio
async def test_handle_resp_slash_class():
    bot = MockBot()

    command_was_run = False

    @bot.include
    @command
    class test_command:
        async def callback(self, ctx: Context):
            nonlocal command_was_run
            command_was_run = True
            assert type(ctx) is test_command.metadata.custom_context

    await handle_resp(MockEvent("test_command", bot))

    assert command_was_run


@mark.asyncio
async def test_hooks():
    bot = MockBot()
    command_was_run = False
    hook_was_run = False
    hook_no_annotations_was_run = False

    async def hook_(ctx: BaseContext):
        nonlocal hook_was_run
        hook_was_run = True
        assert type(ctx) is BaseContext

    async def hook_no_annotations(ctx):
        nonlocal hook_no_annotations_was_run
        hook_no_annotations_was_run = True
        assert type(ctx) is Context

    @bot.include
    @hook(hook_no_annotations)
    @hook(hook_)
    @command
    async def test_command(ctx: Context):
        nonlocal command_was_run
        command_was_run = True
        assert type(ctx) is Context

    await handle_resp(MockEvent("test_command", bot))

    assert hook_was_run
    assert hook_no_annotations_was_run
    assert command_was_run
