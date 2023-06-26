from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from hikari import UNDEFINED, Permissions, UndefinedType

from crescent.commands.hooks import add_hooks
from crescent.exceptions import PermissionsError

if TYPE_CHECKING:
    from typing import Sequence

    from crescent.internal.app_command import AppCommandMeta
    from crescent.internal.includable import Includable
    from crescent.locale import LocaleBuilder
    from crescent.typedefs import HookCallbackT

__all__: Sequence[str] = ("Group", "SubGroup")


def _check_permissions(includable: Includable[AppCommandMeta]) -> None:
    """Raise an exception if permissions are declared in a subcommand."""
    if (
        includable.metadata.app_command.default_member_permissions
        or not includable.metadata.app_command.is_dm_enabled
    ):
        raise PermissionsError(
            "`dm_enabled` and `default_member_permissions` cannot be declared for subcommands."
            " Permissions must be declared in the `crescent.Group` object."
        )


@dataclass
class Group:
    """
    A command group. A command group is a top level command that contains subcommands
    and `SubGroup`s.

    ### Example
    ```python
    import crescent

    utils_group = crescent.Group("utils")

    # This command will appear under the `utils` group in discord.
    @client.include
    @utils_group.child
    @crescent.command
    async def ping(ctx: crescent.Context):
        await ctx.respond("Pong")
    ```
    """

    name: str | LocaleBuilder
    """The name of the group"""
    description: str | LocaleBuilder | None = None
    """The description of the group. The discord API supports this feature but
    it does not do anything."""
    hooks: list[HookCallbackT] | None = None
    """A looks of hooks to run before all commands in this group."""
    after_hooks: list[HookCallbackT] | None = None
    """A list of hooks to run after all commands in this group."""

    default_member_permissions: UndefinedType | int | Permissions = UNDEFINED
    """The default permissions for all commands in this group."""
    dm_enabled: bool = True
    """Whether commands in this group can be used in DMs."""

    def sub_group(
        self,
        name: str | LocaleBuilder,
        description: str | LocaleBuilder | None = None,
        hooks: list[HookCallbackT] | None = None,
        after_hooks: list[HookCallbackT] | None = None,
    ) -> SubGroup:
        """
        Create a sub group from this group.
        """
        return SubGroup(
            name=name, parent=self, description=description, hooks=hooks, after_hooks=after_hooks
        )

    def child(self, includable: Includable[AppCommandMeta]) -> Includable[AppCommandMeta]:
        """
        Add a command to this command group.
        """
        _check_permissions(includable)

        includable.metadata.group = self

        add_hooks(self, includable)

        return includable


@dataclass
class SubGroup:
    """
    A command subgroup. A command subgroup is a group that is under a top level group.

    ### Example
    ```python
    import crescent

    utils_group = crescent.Group("utils")
    time_utils_group = utils_group.sub_group("time")

    # This command will appear under the `utils time` group in discord.
    @client.include
    @time_utils_group.child
    @crescent.command
    async def latency(ctx: crescent.Context):
        await ctx.respond(f"The latency is {bot.heartbeat_latency * 1000}ms")
    ```
    """

    name: str | LocaleBuilder
    parent: Group
    description: str | LocaleBuilder | None = None
    hooks: list[HookCallbackT] | None = None
    """A looks of hooks to run before all commands in this group."""
    after_hooks: list[HookCallbackT] | None = None
    """A list of hooks to run after all commands in this group."""

    def child(self, includable: Includable[AppCommandMeta]) -> Includable[AppCommandMeta]:
        """
        Add a command to this command group.
        """
        _check_permissions(includable)

        includable.metadata.group = self.parent
        includable.metadata.sub_group = self

        add_hooks(self, includable)
        add_hooks(self.parent, includable)

        return includable
