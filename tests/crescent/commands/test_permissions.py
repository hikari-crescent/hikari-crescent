from hikari import PermissionOverwrite
from pytest import raises

from crescent import Context, Group, PermissionsError, command


def test_no_perms_in_subcommand_group():
    group = Group("abcd")

    with raises(PermissionsError):

        @group.child
        @command(dm_enabled=False)
        async def _command(ctx: Context) -> None:
            ...

    with raises(PermissionsError):

        @group.child
        @command(default_member_permissions=PermissionOverwrite(id=0, type=0))
        async def _command(ctx: Context) -> None:
            ...

    @group.child
    @command
    async def _command(ctx: Context) -> None:
        ...


def test_no_perms_in_subcommand_subgroup():
    group = Group("abcd")
    sub_group = group.sub_group("abcd")

    with raises(PermissionsError):

        @sub_group.child
        @command(dm_enabled=False)
        async def _command(ctx: Context) -> None:
            ...

    with raises(PermissionsError):

        @sub_group.child
        @command(default_member_permissions=PermissionOverwrite(id=0, type=0))
        async def _command(ctx: Context) -> None:
            ...

    @sub_group.child
    @command
    async def _command(ctx: Context) -> None:
        ...
