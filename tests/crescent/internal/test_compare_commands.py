from __future__ import annotations

from unittest.mock import Mock

import pytest
from hikari import (
    UNDEFINED,
    ApplicationIntegrationType,
    PartialCommand,
    Permissions,
    SlashCommand,
)

from crescent.internal.app_command import AppCommand

DEFAULT_CONTEXT = ()
DEFAULT_INT = (ApplicationIntegrationType.GUILD_INSTALL,)


@pytest.mark.parametrize(
    ("local_permissions", "remote_permissions", "expected"),
    [
        pytest.param(UNDEFINED, Permissions.NONE, True, id="unset-matches-default"),
        pytest.param(UNDEFINED, Permissions.BAN_MEMBERS, False, id="unset-mismatches-required"),
        pytest.param(0, Permissions.NONE, True, id="explicit-zero"),
        pytest.param(Permissions.NONE, Permissions.NONE, True, id="explicit-none"),
        pytest.param(Permissions.BAN_MEMBERS, Permissions.BAN_MEMBERS, True, id="matching"),
        pytest.param(int(Permissions.BAN_MEMBERS), Permissions.BAN_MEMBERS, True, id="integer"),
        pytest.param(
            Permissions.BAN_MEMBERS, Permissions.NONE, False, id="required-mismatches-default"
        ),
        pytest.param(Permissions.BAN_MEMBERS, Permissions.KICK_MEMBERS, False, id="different"),
    ],
)
def test_compare_commands_default_member_permissions(
    local_permissions, remote_permissions, expected
):
    assert AppCommand(
        type=1,
        name="hello",
        guild_id=None,
        default_member_permissions=local_permissions,
        nsfw=False,
    ).eq_partial_command(
        PartialCommand(
            app=None,
            id=None,
            type=1,
            application_id=None,
            name="hello",
            default_member_permissions=remote_permissions,
            is_nsfw=False,
            guild_id=None,
            version=None,
            name_localizations={},
            context_types=DEFAULT_CONTEXT,
            integration_types=DEFAULT_INT,
        )
    ) is expected


def test_compare_commands_no_options():
    assert AppCommand(
        type=1,
        name="hello",
        guild_id=None,
        default_member_permissions=0,
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
            is_nsfw=False,
            guild_id=None,
            version=None,
            name_localizations={},
            description="desc",
            description_localizations={},
            options=[],
            context_types=DEFAULT_CONTEXT,
            integration_types=DEFAULT_INT,
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
            is_nsfw=False,
            guild_id=None,
            version=None,
            name_localizations={},
            description="desc",
            description_localizations={},
            options=[mock_option_a, mock_option_b, mock_option_c],
            context_types=DEFAULT_CONTEXT,
            integration_types=DEFAULT_INT,
        )
    )

    assert not AppCommand(
        type=1,
        name="hello",
        guild_id=None,
        default_member_permissions=0,
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
            is_nsfw=False,
            guild_id=None,
            version=None,
            name_localizations={},
            description="desc",
            description_localizations={},
            options=[mock_option_a],
            context_types=DEFAULT_CONTEXT,
            integration_types=DEFAULT_INT,
        )
    )
