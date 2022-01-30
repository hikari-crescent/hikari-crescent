from __future__ import annotations

from typing import TYPE_CHECKING

from attr import define

if TYPE_CHECKING:
    from typing import Optional, Sequence, List

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

    def sub_group(self, name: str, description: Optional[str] = None) -> SubGroup:
        return SubGroup(name=name, parent=self, description=description)

    def child(
        self, meta: MetaStruct[CommandCallback, AppCommandMeta]
    ) -> MetaStruct[CommandCallback, AppCommandMeta]:
        meta.metadata.group = self

        if self.hooks:
            meta.interaction_hooks.insert(0, self.hooks)

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
            meta.interaction_hooks.insert(0, self.hooks)

        if self.parent.hooks:
            meta.interaction_hooks.insert(0, self.parent.hooks)

        return meta
