from asyncio import get_event_loop
from typing import List, cast
from unittest.mock import AsyncMock, Mock

from hikari import (
    AutocompleteInteraction,
    AutocompleteInteractionOption,
    CommandChoice,
    CommandInteraction,
    CommandInteractionOption,
    CommandType,
    InteractionCreateEvent,
    InteractionType,
    OptionType,
)
from hikari.impl import RESTClientImpl
from pytest import mark

from crescent import Context, catch_autocomplete, catch_command, command, hook
import crescent
from crescent.commands.options import option
from crescent.exceptions import ConverterExceptionMeta, ConverterExceptions
from crescent.internal.handle_resp import handle_resp
from tests.utils import MockClient, MockRESTClient


def MockEvent(name, client, arg: str | None = None):
    if arg:
        options = (
            CommandInteractionOption(
                name="arg", type=OptionType.STRING, value=arg, options=None
            ),
        )
    else:
        options = None

    return InteractionCreateEvent(
        shard=None,
        interaction=CommandInteraction(
            app=client.app,
            id=None,
            application_id=...,
            type=InteractionType.APPLICATION_COMMAND,
            token=None,
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
            options=options,
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


@mark.asyncio
async def test_converter_ok() -> None:
    client = MockClient()

    arg_val = None

    @client.include
    @command
    class test_command:
        arg = option(str).convert(int)

        async def callback(self, ctx: Context) -> None:
            nonlocal arg_val
            arg_val = self.arg

    await handle_resp(client, MockEvent("test_command", client, "1").interaction, None)

    assert arg_val == 1


@mark.asyncio
async def test_converter_error() -> None:
    client = MockClient()

    arg_val = None
    exc: "ConverterExceptions | None" = None

    @client.include
    @catch_command(ConverterExceptions)
    async def error(_exc: ConverterExceptions, ctx:  Context) -> None:
        nonlocal exc
        exc = _exc

    class test_command:
        arg = option(str).convert(int)

        async def callback(self, ctx: Context) -> None:
            nonlocal arg_val
            arg_val = self.arg

    client.include(command(test_command))

    await handle_resp(client, MockEvent("test_command", client, "oops").interaction, None)

    assert arg_val is None
    assert exc is not None

    exc = cast("ConverterExceptions", exc)
    assert len(exc.errors) == 1

    meta = exc.errors[0]
    assert meta.option_key == "arg"
    assert meta.value == "oops"
    assert meta.command is test_command


@mark.asyncio
async def test_handle_resp_slash_function():
    client = MockClient()

    command_was_run = False

    @client.include
    @command
    async def test_command(ctx: Context):
        nonlocal command_was_run
        command_was_run = True

    await handle_resp(client, MockEvent("test_command", client).interaction, None)

    assert command_was_run


@mark.asyncio
async def test_handle_resp_slash_class():
    client = MockClient()

    command_was_run = False

    @client.include
    @command
    class test_command:
        async def callback(self, ctx: Context):
            nonlocal command_was_run
            command_was_run = True

    await handle_resp(client, MockEvent("test_command", client).interaction, None)

    assert command_was_run


@mark.asyncio
async def test_hooks():
    client = MockClient()
    command_was_run = False
    hook_was_run = False
    hook_no_annotations_was_run = False

    mock_id = Mock()

    async def hook_(ctx: Context):
        nonlocal hook_was_run
        hook_was_run = True

        ctx.id = mock_id

    async def hook_no_annotations(ctx):
        nonlocal hook_no_annotations_was_run
        hook_no_annotations_was_run = True
        assert type(ctx) is Context

    @client.include
    @hook(hook_no_annotations)
    @hook(hook_)
    @command
    async def test_command(ctx: Context):
        nonlocal command_was_run
        command_was_run = True
        assert ctx.id is mock_id

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
    async def test_command_handler(exc: Exception, ctx: Context):
        nonlocal error_handler_was_run
        error_handler_was_run = True
        assert isinstance(exc, Exception)

    @client.include
    @command
    async def test_command(ctx: Context):
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
    async def test_command_handler(exc: ValueError, ctx: Context):
        nonlocal error_handler_was_run
        error_handler_was_run = True

    @client.include
    @command
    async def test_command(ctx: Context):
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
        exc: Exception, ctx: Context, options: AutocompleteInteractionOption
    ):
        nonlocal error_handler_was_run
        assert type(exc) is Exception
        error_handler_was_run = True

    async def autocomplete_resp(
        ctx: Context, option: AutocompleteInteractionOption
    ) -> List[CommandChoice]:
        nonlocal autocomplete_was_run
        autocomplete_was_run = True
        raise Exception

    @client.include
    @command(name="test_command")
    class TestCommand:
        option = crescent.option(str, autocomplete=autocomplete_resp)

        def callback(ctx: Context):
            nonlocal command_was_run
            command_was_run = True

    await handle_resp(
        client,
        MockAutocompleteEvent("test_command", "option", client).interaction,
        None,
    )

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
        ctx: Context, option: AutocompleteInteractionOption
    ) -> List[CommandChoice]:
        nonlocal autocomplete_was_run
        autocomplete_was_run = True
        raise TypeError

    @client.include
    @command(name="test_command")
    class TestCommand:
        option = crescent.option(str, autocomplete=autocomplete_resp)

        def callback(ctx: Context):
            nonlocal command_was_run
            command_was_run = True

    await handle_resp(
        client,
        MockAutocompleteEvent("test_command", "option", client).interaction,
        None,
    )

    assert autocomplete_was_run
    assert not error_handler_was_run
    assert not command_was_run


@mark.asyncio
async def test_rest_bot_command():
    client = MockRESTClient()

    command_was_run = False

    create_interaction_response = AsyncMock()

    RESTClientImpl.create_interaction_response = create_interaction_response

    @client.include
    @command
    async def test_command(ctx: Context):
        nonlocal command_was_run
        command_was_run = True

        await ctx.respond("something")

    await handle_resp(
        client,
        MockEvent("test_command", client).interaction,
        future=get_event_loop().create_future(),
    )

    create_interaction_response.assert_not_called()

    assert command_was_run


@mark.asyncio
async def test_rest_future_is_set():
    client = MockRESTClient()

    mock_future = Mock()
    set_result = Mock()
    done = Mock(return_value=False)
    mock_future.set_result = set_result
    mock_future.done = done

    @client.include
    @command
    async def test_command(ctx: Context):
        await ctx.defer()
        print(ctx._rest_interaction_future.set_result)
        await ctx.followup("something")

    await handle_resp(
        client, MockEvent("test_command", client).interaction, future=mock_future
    )

    set_result.assert_called_once()
