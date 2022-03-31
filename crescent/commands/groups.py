from __future__ import annotations

from typing import TYPE_CHECKING

from attr import define

if TYPE_CHECKING:
    from typing import List, Optional, Sequence

    from crescent.internal.app_command import AppCommandMeta
    from crescent.internal.meta_struct import MetaStruct
    from crescent.typedefs import CommandCallbackT, HookCallbackT

__all__: Sequence[str] = ("Group", "SubGroup")


@define
class Group:
    """A slash command group."""

    name: str
    """The name of the group."""
    description: Optional[str] = None
    """The description of the group."""
    hooks: Optional[List[HookCallbackT]] = None
    """The hooks of the group."""

    def sub_group(
        self,
        name: str,
        description: Optional[str] = None,
        hooks: Optional[List[HookCallbackT]] = None,
    ) -> SubGroup:
        """Create a sub group.

        Args:
            name: The name of the sub group.
            description: The description of the sub group. Defaults to None.
            hooks: The hooks for the sub group. Defaults to None.

        Returns:
            The sub group.
        """

        return SubGroup(name=name, parent=self, description=description, hooks=hooks)

    def child(
        self, meta: MetaStruct[CommandCallbackT, AppCommandMeta]
    ) -> MetaStruct[CommandCallbackT, AppCommandMeta]:
        """Include a command in the group."""

        meta.metadata.group = self

        if self.hooks:
            meta.metadata.hooks = self.hooks + meta.metadata.hooks

        return meta


@define
class SubGroup:
    """A slash command sub group."""

    name: str
    """The name of the sub group."""
    parent: Group
    """The parent group."""
    description: Optional[str] = None
    """The description of the sub group."""
    hooks: Optional[List[HookCallbackT]] = None
    """The hooks of the sub group."""

    def child(
        self, meta: MetaStruct[CommandCallbackT, AppCommandMeta]
    ) -> MetaStruct[CommandCallbackT, AppCommandMeta]:
        """Include a command in the sub group."""

        meta.metadata.group = self.parent
        meta.metadata.sub_group = self

        if self.hooks:
            meta.metadata.hooks = self.hooks + meta.metadata.hooks

        if self.parent.hooks:
            meta.metadata.hooks = meta.metadata.hooks + self.parent.hooks

        return meta
