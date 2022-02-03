from __future__ import annotations

from typing import TYPE_CHECKING

from attr import define

if TYPE_CHECKING:
    from typing import List, Optional, Sequence

    from crescent.internal.app_command import AppCommandMeta
    from crescent.internal.meta_struct import MetaStruct
    from crescent.typedefs import CommandCallback, HookCallbackT

__all__: Sequence[str] = (
    "Group",
    "SubGroup",
)


@define
class Group:
    name: str
    description: Optional[str] = None
    hooks: Optional[List[HookCallbackT]] = None

    def sub_group(
        self,
        name: str,
        description: Optional[str] = None,
        hooks: Optional[List[HookCallbackT]] = None,
    ) -> SubGroup:
        return SubGroup(
            name=name,
            parent=self,
            description=description,
            hooks=hooks,
        )

    def child(
        self, meta: MetaStruct[CommandCallback, AppCommandMeta]
    ) -> MetaStruct[CommandCallback, AppCommandMeta]:
        meta.metadata.group = self

        if self.hooks:
            meta.interaction_hooks = self.hooks + meta.interaction_hooks

        return meta


@define
class SubGroup:
    name: str
    parent: Group
    description: Optional[str] = None
    hooks: Optional[List[HookCallbackT]] = None

    def child(
        self, meta: MetaStruct[CommandCallback, AppCommandMeta]
    ) -> MetaStruct[CommandCallback, AppCommandMeta]:
        meta.metadata.group = self.parent
        meta.metadata.sub_group = self

        if self.hooks:
            meta.interaction_hooks = self.hooks + meta.interaction_hooks

        if self.parent.hooks:
            meta.interaction_hooks = self.parent.hooks + meta.interaction_hooks

        return meta
