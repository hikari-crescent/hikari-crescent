from hikari import UNDEFINED, Message, Permissions, User

from crescent import Context, command, message_command, user_command


def test_defaults():
    @command
    async def test_command(ctx: Context):
        ...

    assert test_command.metadata.app_command.name == "test_command"
    assert test_command.metadata.app_command.guild_id is None
    assert test_command.metadata.app_command.description == "No Description"
    assert test_command.metadata.app_command.default_member_permissions is UNDEFINED
    assert test_command.metadata.app_command.is_dm_enabled
    assert test_command.metadata.app_command.nsfw is None


def test_user_command_defaults():
    @user_command
    async def test_command(ctx: Context, user: User):
        ...

    assert test_command.metadata.app_command.name == "test_command"
    assert test_command.metadata.app_command.guild_id is None
    assert test_command.metadata.app_command.default_member_permissions is UNDEFINED
    assert test_command.metadata.app_command.is_dm_enabled
    assert test_command.metadata.app_command.nsfw is None


def test_message_command_defaults():
    @user_command
    async def test_command(ctx: Context, user: Message):
        ...

    assert test_command.metadata.app_command.name == "test_command"
    assert test_command.metadata.app_command.guild_id is None
    assert test_command.metadata.app_command.default_member_permissions is UNDEFINED
    assert test_command.metadata.app_command.is_dm_enabled
    assert test_command.metadata.app_command.nsfw is None


def test_not_default():
    @command(
        name="test_name",
        guild=123456,
        description="test description",
        default_member_permissions=Permissions.BAN_MEMBERS,
        dm_enabled=False,
        nsfw=True,
    )
    async def test_command(ctx: Context):
        ...

    assert test_command.metadata.app_command.name == "test_name"
    assert test_command.metadata.app_command.guild_id == 123456
    assert test_command.metadata.app_command.description == "test description"
    assert test_command.metadata.app_command.default_member_permissions is Permissions.BAN_MEMBERS
    assert not test_command.metadata.app_command.is_dm_enabled
    assert test_command.metadata.app_command.nsfw


def test_message_command_not_default():
    @message_command(
        name="Test Name",
        guild=123456,
        default_member_permissions=Permissions.BAN_MEMBERS,
        dm_enabled=False,
        nsfw=True,
    )
    async def test_command(ctx: Context):
        ...

    assert test_command.metadata.app_command.name == "Test Name"
    assert test_command.metadata.app_command.guild_id == 123456
    assert test_command.metadata.app_command.default_member_permissions is Permissions.BAN_MEMBERS
    assert not test_command.metadata.app_command.is_dm_enabled
    assert test_command.metadata.app_command.nsfw


def test_user_command_not_default():
    @user_command(
        name="Test Name",
        guild=123456,
        default_member_permissions=Permissions.BAN_MEMBERS,
        dm_enabled=False,
        nsfw=True,
    )
    async def test_command(ctx: Context):
        ...

    assert test_command.metadata.app_command.name == "Test Name"
    assert test_command.metadata.app_command.guild_id == 123456
    assert test_command.metadata.app_command.default_member_permissions is Permissions.BAN_MEMBERS
    assert not test_command.metadata.app_command.is_dm_enabled
    assert test_command.metadata.app_command.nsfw
