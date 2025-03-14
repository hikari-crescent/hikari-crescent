from hikari import CommandType, Permissions
from hikari.impl.entity_factory import EntityFactoryImpl

from crescent.internal.app_command import AppCommand
from tests.utils import MockBot

FACTORY = EntityFactoryImpl(MockBot())


def test_build_no_perms():
    assert AppCommand(
        type=CommandType.SLASH, name="test_command", description="test description", guild_id=1234
    ).build(FACTORY) == {
        "name": "test_command",
        "name_localizations": {},
        "type": CommandType.SLASH,
        "description": "test description",
        "description_localizations": {},
        "dm_permission": True,
    }


def test_build_denied_all_perms():
    assert AppCommand(
        type=CommandType.SLASH,
        name="test_command",
        description="test description",
        guild_id=1234,
        default_member_permissions=Permissions.NONE,
    ).build(FACTORY) == {
        "name": "test_command",
        "name_localizations": {},
        "type": CommandType.SLASH,
        "description": "test description",
        "description_localizations": {},
        "dm_permission": True,
        "default_member_permissions": "0",
    }


def test_build_with_perms():
    assert AppCommand(
        type=CommandType.SLASH,
        name="test_command",
        description="test description",
        default_member_permissions=Permissions.ATTACH_FILES,
        is_dm_enabled=False,
        guild_id=1234,
    ).build(FACTORY) == {
        "name": "test_command",
        "name_localizations": {},
        "type": CommandType.SLASH,
        "description": "test description",
        "description_localizations": {},
        "default_member_permissions": str(Permissions.ATTACH_FILES.value),
        "dm_permission": False,
    }

    assert AppCommand(
        type=CommandType.SLASH,
        name="test_command",
        description="test description",
        default_member_permissions=32768,
        is_dm_enabled=False,
        guild_id=1234,
    ).build(FACTORY) == {
        "name": "test_command",
        "name_localizations": {},
        "type": CommandType.SLASH,
        "description": "test description",
        "description_localizations": {},
        "default_member_permissions": str(32768),
        "dm_permission": False,
    }
