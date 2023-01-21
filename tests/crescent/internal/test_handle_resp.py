from typing import List
from unittest.mock import Mock

from hikari import (
    AutocompleteInteraction,
    AutocompleteInteractionOption,
    CommandChoice,
    CommandInteraction,
    CommandType,
    InteractionCreateEvent,
    InteractionType,
    OptionType,
)
from pytest import mark
from typing_extensions import Annotated

from crescent import (
    Autocomplete,
    BaseContext,
    Context,
    catch_autocomplete,
    catch_command,
    command,
    hook,
)
from crescent.internal.handle_resp import handle_resp
from tests.utils import MockClient


def MockEvent(name, client):
    return InteractionCreateEvent(
        shard=None,
        interaction=CommandInteraction(
            app=client.app,
            id=None,
            application_id=...,
            type=InteractionType.APPLICATION_COMMAND,
            token=client.app._token,
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
            app_permissions=None,
        ),
    )


def MockAutocompleteEvent(name, option_name, client):
    return InteractionCreateEvent(
        shard=None,
        interaction=AutocompleteInteraction(
            app=client.app,
            id=None,
            application_id=...,
            type=InteractionType.AUTOCOMPLETE,
            token=client.app._token,
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
            options=[
                AutocompleteInteractionOption(
                    name=option_name,
                    type=OptionType.STRING,
                    value="abcd",
                    is_focused=True,
                    options=None,
                )
            ],
        ),
    )


class CustomContext(BaseContext):
    ...


@mark.asyncio
async def test_handle_resp_slash_function():
    client = MockClient()

    command_was_run = False

    @client.include
    @command
    async def test_command(ctx: CustomContext):
        nonlocal command_was_run
        command_was_run = True
        assert type(ctx) is test_command.metadata.custom_context

    await handle_resp(client, MockEvent("test_command", client).interaction, None)

    assert command_was_run


@mark.asyncio
async def test_handle_resp_slash_class():
    client = MockClient()

    command_was_run = False

    @client.include
    @command
    class test_command:
        async def callback(self, ctx: CustomContext):
            nonlocal command_was_run
            command_was_run = True
            assert type(ctx) is test_command.metadata.custom_context

    await handle_resp(client, MockEvent("test_command", client).interaction, None)

    assert command_was_run


@mark.asyncio
async def test_hooks():
    client = MockClient()
    command_was_run = False
    hook_was_run = False
    hook_no_annotations_was_run = False

    mock_id = Mock()

    async def hook_(ctx: CustomContext):
        nonlocal hook_was_run
        hook_was_run = True

        ctx.id = mock_id

        assert type(ctx) is CustomContext

    async def hook_no_annotations(ctx):
        nonlocal hook_no_annotations_was_run
        hook_no_annotations_was_run = True
        assert type(ctx) is Context

    @client.include
    @hook(hook_no_annotations)
    @hook(hook_)
    @command
    async def test_command(ctx: CustomContext):
        nonlocal command_was_run
        command_was_run = True
        assert ctx.id is mock_id
        assert type(ctx) is CustomContext

    await handle_resp(client, MockEvent("test_command", client).interaction, None)

    assert hook_was_run
    assert hook_no_annotations_was_run
    assert command_was_run


@mark.asyncio
async def test_handle_command_error():
    client = MockClient()
    command_was_run = False
    error_handler_was_run = False

    @client.include
    @catch_command(Exception)
    async def test_command_handler(exc: Exception, ctx: CustomContext):
        nonlocal error_handler_was_run
        error_handler_was_run = True
        assert isinstance(exc, Exception)
        assert type(ctx) is CustomContext

    @client.include
    @command
    async def test_command(ctx: CustomContext):
        nonlocal command_was_run
        command_was_run = True
        raise Exception

    await handle_resp(client, MockEvent("test_command", client).interaction, None)

    assert error_handler_was_run
    assert command_was_run


@mark.asyncio
async def test_unhandled_command_error():
    client = MockClient()
    command_was_run = False
    error_handler_was_run = False

    @client.include
    @catch_command(ValueError)
    async def test_command_handler(exc: ValueError, ctx: CustomContext):
        nonlocal error_handler_was_run
        assert type(ctx) is CustomContext
        error_handler_was_run = True

    @client.include
    @command
    async def test_command(ctx: CustomContext):
        nonlocal command_was_run
        command_was_run = True
        raise TypeError

    await handle_resp(client, MockEvent("test_command", client).interaction, None)

    assert not error_handler_was_run
    assert command_was_run


@mark.asyncio
async def test_handle_autocomplete_error():
    client = MockClient()
    command_was_run = False
    error_handler_was_run = False
    autocomplete_was_run = False

    @client.include
    @catch_autocomplete(Exception)
    async def test_command_handler(
        exc: Exception, ctx: CustomContext, options: AutocompleteInteractionOption
    ):
        nonlocal error_handler_was_run
        assert type(ctx) is CustomContext
        assert type(exc) is Exception
        error_handler_was_run = True

    async def autocomplete_resp(
        ctx: CustomContext, option: AutocompleteInteractionOption
    ) -> List[CommandChoice]:
        nonlocal autocomplete_was_run
        autocomplete_was_run = True
        assert type(ctx) is CustomContext
        raise Exception

    @client.include
    @command
    async def test_command(
        ctx: CustomContext, option: Annotated[str, Autocomplete(autocomplete_resp)]
    ):
        nonlocal command_was_run
        command_was_run = True

    await handle_resp(client, MockAutocompleteEvent("test_command", "option", client).interaction, None)

    assert error_handler_was_run
    assert autocomplete_was_run
    assert not command_was_run


@mark.asyncio
async def test_unhandled_autocomplete_error():
    client = MockClient()
    command_was_run = False
    error_handler_was_run = False
    autocomplete_was_run = False

    @client.include
    @catch_autocomplete(ValueError)
    async def test_command_handler(
        exc: Exception, ctx: ValueError, options: AutocompleteInteractionOption
    ):
        nonlocal error_handler_was_run
        error_handler_was_run = True

    async def autocomplete_resp(
        ctx: CustomContext, option: AutocompleteInteractionOption
    ) -> List[CommandChoice]:
        nonlocal autocomplete_was_run
        autocomplete_was_run = True
        raise TypeError

    @client.include
    @command
    async def test_command(
        ctx: CustomContext, option: Annotated[str, Autocomplete(autocomplete_resp)]
    ):
        nonlocal command_was_run
        command_was_run = True

    await handle_resp(client, MockAutocompleteEvent("test_command", "option", client).interaction, None)

    assert autocomplete_was_run
    assert not error_handler_was_run
    assert not command_was_run
