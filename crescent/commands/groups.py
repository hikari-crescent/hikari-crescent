from __future__ import annotations

from typing import TYPE_CHECKING

from attr import define

if TYPE_CHECKING:
    from typing import Sequence

    from crescent.internal.app_command import AppCommandMeta
    from crescent.internal.meta_struct import MetaStruct
    from crescent.typedefs import CommandCallbackT, HookCallbackT

__all__: Sequence[str] = ("Group", "SubGroup")


@define
class Group:
    name: str
    description: str | None = None
    hooks: list[HookCallbackT] | None = None
    after_hooks: list[HookCallbackT] | None = None

    def sub_group(
        self,
        name: str,
        description: str | None = None,
        hooks: list[HookCallbackT] | None = None,
        after_hooks: list[HookCallbackT] | None = None,
    ) -> SubGroup:
        return SubGroup(
            name=name, parent=self, description=description, hooks=hooks, after_hooks=after_hooks
        )

    def child(
        self, meta: MetaStruct[CommandCallbackT, AppCommandMeta]
    ) -> MetaStruct[CommandCallbackT, AppCommandMeta]:
        meta.metadata.group = self

        if self.hooks:
            meta.metadata.hooks = self.hooks + meta.metadata.hooks

        if self.after_hooks:
            meta.metadata.after_hooks = self.after_hooks + meta.metadata.after_hooks

        return meta


@define
class SubGroup:
    name: str
    parent: Group
    description: str | None = None
    hooks: list[HookCallbackT] | None = None
    after_hooks: list[HookCallbackT] | None = None

    def child(
        self, meta: MetaStruct[CommandCallbackT, AppCommandMeta]
    ) -> MetaStruct[CommandCallbackT, AppCommandMeta]:
        meta.metadata.group = self.parent
        meta.metadata.sub_group = self

        if self.hooks:
            meta.metadata.hooks = self.hooks + meta.metadata.hooks
        if self.parent.hooks:
            meta.metadata.hooks = meta.metadata.hooks + self.parent.hooks

        if self.after_hooks:
            meta.metadata.after_hooks = self.after_hooks + meta.metadata.after_hooks
        if self.parent.after_hooks:
            meta.metadata.after_hooks = meta.metadata.after_hooks + self.parent.after_hooks

        return meta
