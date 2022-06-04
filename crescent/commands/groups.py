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
    name: str
    description: Optional[str] = None
    hooks: Optional[List[HookCallbackT]] = None
    hook_after: Optional[List[HookCallbackT]] = None

    def sub_group(
        self,
        name: str,
        description: Optional[str] = None,
        hooks: Optional[List[HookCallbackT]] = None,
        hook_after: Optional[List[HookCallbackT]] = None,
    ) -> SubGroup:
        return SubGroup(
            name=name, parent=self, description=description, hooks=hooks, hook_after=hook_after
        )

    def child(
        self, meta: MetaStruct[CommandCallbackT, AppCommandMeta]
    ) -> MetaStruct[CommandCallbackT, AppCommandMeta]:
        meta.metadata.group = self

        if self.hooks:
            meta.metadata.hooks = self.hooks + meta.metadata.hooks

        if self.hook_after:
            meta.metadata.after_hooks = self.hook_after + meta.metadata.after_hooks

        return meta


@define
class SubGroup:
    name: str
    parent: Group
    description: Optional[str] = None
    hooks: Optional[List[HookCallbackT]] = None
    hook_after: Optional[List[HookCallbackT]] = None

    def child(
        self, meta: MetaStruct[CommandCallbackT, AppCommandMeta]
    ) -> MetaStruct[CommandCallbackT, AppCommandMeta]:
        meta.metadata.group = self.parent
        meta.metadata.sub_group = self

        if self.hooks:
            meta.metadata.hooks = self.hooks + meta.metadata.hooks
        if self.parent.hooks:
            meta.metadata.hooks = meta.metadata.hooks + self.parent.hooks

        if self.hook_after:
            meta.metadata.after_hooks = self.hook_after + meta.metadata.after_hooks
        if self.parent.hook_after:
            meta.metadata.after_hooks = meta.metadata.after_hooks + self.parent.hook_after

        return meta
