from copy import copy
from unittest.mock import AsyncMock, Mock

from hikari import CommandInteractionOption, InteractionType, OptionType
from hikari.impl import CacheImpl, RESTClientImpl
from pytest import mark

from crescent import AutocompleteContext
from crescent.mentionable import Mentionable
from tests.utils import MockBot, MockClient

options = [
    CommandInteractionOption(name="user", type=OptionType.USER, value=12345, options=None),
    CommandInteractionOption(
        name="mentionable", type=OptionType.MENTIONABLE, value=12345, options=None
    ),
    CommandInteractionOption(name="channel", type=OptionType.CHANNEL, value=12345, options=None),
    CommandInteractionOption(
        name="attachment", type=OptionType.ATTACHMENT, value=12345, options=None
    ),
]

options_with_role = copy(options)
options_with_role.append(
    CommandInteractionOption(name="role", type=OptionType.ROLE, value=12345, options=None)
)

interaction = Mock()
interaction.type = InteractionType.AUTOCOMPLETE
interaction.options = options

ctx = AutocompleteContext(
    client=MockClient(),
    app=MockBot(),
    application_id=None,
    type=None,
    token=None,
    id=None,
    version=None,
    channel_id=None,
    guild_id=None,
    user=None,
    group=None,
    sub_group=None,
    member=None,
    locale=None,
    command_type=None,
    options=None,
    _has_created_message=None,
    _has_deferred_response=None,
    command=None,
    interaction=interaction,
    _rest_interaction_future=None,
)


guild_ctx = copy(ctx)
guild_ctx.interaction = copy(ctx.interaction)

guild_ctx.guild_id = 12345
guild_ctx.interaction.guild_id = 1234
guild_ctx.interaction.options = options_with_role


@mark.asyncio
async def test_fetch_options_not_cached():
    fetch_member_mock = AsyncMock(return_value="member")
    fetch_user_mock = AsyncMock(return_value="user")
    fetch_channel_mock = AsyncMock(return_value="channel")

    RESTClientImpl._get_live_attributes = Mock()
    RESTClientImpl.fetch_member = fetch_member_mock
    RESTClientImpl.fetch_user = fetch_user_mock
    RESTClientImpl.fetch_channel = fetch_channel_mock

    get_member_mock = Mock(return_value=None)
    get_user_mock = Mock(return_value=None)
    get_guild_channel_mock = Mock(return_value=None)

    CacheImpl.get_member = get_member_mock
    CacheImpl.get_user = get_user_mock
    CacheImpl.get_guild_channel = get_guild_channel_mock

    res = await ctx.fetch_options()

    fetch_member_mock.assert_not_called()
    fetch_user_mock.assert_called_with(12345)
    assert fetch_user_mock.call_count == 2
    fetch_channel_mock.assert_called_once_with(12345)

    get_member_mock.assert_not_called()
    get_user_mock.assert_called_with(12345)
    assert get_user_mock.call_count == 2
    get_guild_channel_mock.assert_called_once_with(12345)

    assert res == {
        "user": "user",
        "channel": "channel",
        "mentionable": Mentionable(user="user", role=None),
        "attachment": None,
    }


@mark.asyncio
async def test_fetch_options_guild_not_cached():
    fetch_member_mock = AsyncMock(return_value="member")
    fetch_user_mock = AsyncMock(return_value="user")

    role_mock = Mock()
    role_mock.id = 12345

    fetch_roles_mock = AsyncMock(return_value=[role_mock])
    fetch_channel_mock = AsyncMock(return_value="channel")

    RESTClientImpl._get_live_attributes = Mock()
    RESTClientImpl.fetch_member = fetch_member_mock
    RESTClientImpl.fetch_user = fetch_user_mock
    RESTClientImpl.fetch_roles = fetch_roles_mock
    RESTClientImpl.fetch_channel = fetch_channel_mock

    get_member_mock = Mock(return_value=None)
    get_user_mock = Mock(return_value=None)
    get_guild_channel_mock = Mock(return_value=None)
    get_role_mock = Mock(return_value=None)

    CacheImpl.get_member = get_member_mock
    CacheImpl.get_user = get_user_mock
    CacheImpl.get_guild_channel = get_guild_channel_mock
    CacheImpl.get_role = get_role_mock

    res = await guild_ctx.fetch_options()

    fetch_member_mock.assert_called_with(guild_ctx.guild_id, 12345)
    assert fetch_member_mock.call_count == 2
    fetch_user_mock.assert_not_called()
    fetch_roles_mock.assert_called_with(guild_ctx.guild_id)
    fetch_channel_mock.assert_called_once_with(12345)

    get_member_mock.assert_called_with(guild_ctx.guild_id, 12345)
    assert get_member_mock.call_count == 2
    get_user_mock.assert_not_called()
    get_guild_channel_mock.assert_called_once_with(12345)
    get_role_mock.assert_called_once_with(12345)

    assert res == {
        "user": "member",
        "channel": "channel",
        "role": role_mock,
        "mentionable": Mentionable(user="member", role=None),
        "attachment": None,
    }


@mark.asyncio
async def test_fetch_options_cached():
    get_member_mock = Mock(return_value="member")
    get_user_mock = Mock(return_value="user")
    get_guild_channel_mock = Mock(return_value="channel")

    CacheImpl.get_member = get_member_mock
    CacheImpl.get_user = get_user_mock
    CacheImpl.get_guild_channel = get_guild_channel_mock

    res = await ctx.fetch_options()

    get_member_mock.assert_not_called()
    get_user_mock.assert_called_with(12345)
    assert get_user_mock.call_count == 2
    get_guild_channel_mock.assert_called_once_with(12345)

    assert res == {
        "user": "user",
        "channel": "channel",
        "mentionable": Mentionable(user="user", role=None),
        "attachment": None,
    }


@mark.asyncio
async def test_fetch_options_guild_cached():
    role_mock = Mock()
    role_mock.id = 12345

    get_member_mock = Mock(return_value="member")
    get_user_mock = Mock(return_value="user")
    get_guild_channel_mock = Mock(return_value="channel")
    get_role_mock = Mock(return_value=role_mock)

    CacheImpl.get_member = get_member_mock
    CacheImpl.get_user = get_user_mock
    CacheImpl.get_guild_channel = get_guild_channel_mock
    CacheImpl.get_role = get_role_mock

    res = await guild_ctx.fetch_options()

    get_member_mock.assert_called_with(guild_ctx.guild_id, 12345)
    assert get_member_mock.call_count == 2
    get_user_mock.assert_not_called()
    get_guild_channel_mock.assert_called_once_with(12345)
    get_role_mock.assert_called_once_with(12345)

    assert res == {
        "user": "member",
        "channel": "channel",
        "mentionable": Mentionable(user="member", role=None),
        "role": role_mock,
        "attachment": None,
    }
