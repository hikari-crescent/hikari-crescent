from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Iterable

from hikari import UNDEFINED, ApplicationContextType, Permissions, UndefinedType

from crescent.exceptions import PermissionsError

if TYPE_CHECKING:
    from typing import Sequence

    from crescent.internal.app_command import AppCommandMeta
    from crescent.internal.includable import Includable
    from crescent.locale import LocaleBuilder
    from crescent.typedefs import CommandHookCallbackT

__all__: Sequence[str] = ("Group", "SubGroup")


def _check_permissions(includable: Includable[AppCommandMeta]) -> None:
    """Raise an exception if permissions are declared in a subcommand."""
    if includable.metadata.app_command.default_member_permissions:
        raise PermissionsError(
            "`default_member_permissions` cannot be declared for subcommands."
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
    hooks: list[CommandHookCallbackT] = field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]
    """A looks of hooks to run before all commands in this group."""
    after_hooks: list[CommandHookCallbackT] = field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]
    """A list of hooks to run after all commands in this group."""

    default_member_permissions: UndefinedType | int | Permissions = UNDEFINED
    """The default permissions for all commands in this group."""
    context_types: UndefinedType | Iterable[ApplicationContextType] = UNDEFINED
    """The contexts in which the command can be used."""

    def sub_group(
        self,
        name: str | LocaleBuilder,
        description: str | LocaleBuilder | None = None,
        hooks: list[CommandHookCallbackT] | None = None,
        after_hooks: list[CommandHookCallbackT] | None = None,
    ) -> SubGroup:
        """
        Create a sub group from this group.
        """
        return SubGroup(
            name=name,
            parent=self,
            description=description,
            hooks=hooks or [],
            after_hooks=after_hooks or [],
        )

    def child(self, includable: Includable[AppCommandMeta]) -> Includable[AppCommandMeta]:
        """
        Add a command to this command group.
        """
        _check_permissions(includable)

        includable.metadata.group = self

        includable.metadata.add_hooks(self.hooks, after=False)
        includable.metadata.add_hooks(self.after_hooks, after=True)

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
    hooks: list[CommandHookCallbackT] = field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]
    """A looks of hooks to run before all commands in this group."""
    after_hooks: list[CommandHookCallbackT] = field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]
    """A list of hooks to run after all commands in this group."""

    def child(self, includable: Includable[AppCommandMeta]) -> Includable[AppCommandMeta]:
        """
        Add a command to this command group.
        """
        _check_permissions(includable)

        includable.metadata.group = self.parent
        includable.metadata.sub_group = self

        includable.metadata.add_hooks(self.hooks, after=False)
        includable.metadata.add_hooks(self.after_hooks, after=True)
        includable.metadata.add_hooks(self.parent.hooks, after=False)
        includable.metadata.add_hooks(self.parent.after_hooks, after=True)

        return includable
