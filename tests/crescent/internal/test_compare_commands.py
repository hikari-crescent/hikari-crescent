from unittest.mock import Mock

from hikari.events import guild_events
from crescent.internal.app_command import AppCommand

from hikari import PartialCommand, Permissions, SlashCommand


def test_compare_commands():
    assert AppCommand(
        type=1,
        name="hello",
        guild_id=None,
        default_member_permissions=0,
        is_dm_enabled=True,
        nsfw=False,
    ).eq_partial_command(
        PartialCommand(
            app=None,
            id=None,
            type=1,
            application_id=None,
            name="hello",
            default_member_permissions=Permissions(0),
            is_dm_enabled=True,
            is_nsfw=False,
            guild_id=None,
            version=None,
            name_localizations={},
        )
    )


def test_compare_commands_no_options():
    assert AppCommand(
        type=1,
        name="hello",
        guild_id=None,
        default_member_permissions=0,
        is_dm_enabled=True,
        nsfw=False,
        description="desc",
        options=[],
    ).eq_partial_command(
        SlashCommand(
            app=None,
            id=None,
            type=1,
            application_id=None,
            name="hello",
            default_member_permissions=Permissions(0),
            is_dm_enabled=True,
            is_nsfw=False,
            guild_id=None,
            version=None,
            name_localizations={},
            description="desc",
            description_localizations={},
            options=[],
        )
    )


def test_compare_should_succeed_with_options():
    # Not testing eq for options, because that is implemented by hikari.
    mock_option_a = Mock()
    mock_option_b = Mock()
    mock_option_c = Mock()

    mock_option_a.__eq__ = lambda _: True
    mock_option_b.__eq__ = lambda _: True
    mock_option_c.__eq__ = lambda _: True

    assert AppCommand(
        type=1,
        name="hello",
        guild_id=None,
        default_member_permissions=0,
        is_dm_enabled=True,
        nsfw=False,
        description="desc",
        options=[mock_option_a, mock_option_b, mock_option_c],
    ).eq_partial_command(
        SlashCommand(
            app=None,
            id=None,
            type=1,
            application_id=None,
            name="hello",
            default_member_permissions=Permissions(0),
            is_dm_enabled=True,
            is_nsfw=False,
            guild_id=None,
            version=None,
            name_localizations={},
            description="desc",
            description_localizations={},
            options=[mock_option_a, mock_option_b, mock_option_c],
        )
    )

    assert not AppCommand(
        type=1,
        name="hello",
        guild_id=None,
        default_member_permissions=0,
        is_dm_enabled=True,
        nsfw=False,
        description="desc",
        options=[],
    ).eq_partial_command(
        SlashCommand(
            app=None,
            id=None,
            type=1,
            application_id=None,
            name="hello",
            default_member_permissions=Permissions(0),
            is_dm_enabled=True,
            is_nsfw=False,
            guild_id=None,
            version=None,
            name_localizations={},
            description="desc",
            description_localizations={},
            options=[mock_option_a],
        )
    )
