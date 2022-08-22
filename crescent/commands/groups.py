from __future__ import annotations

from typing import TYPE_CHECKING

from attr import define

from crescent.commands.hooks import add_hooks

if TYPE_CHECKING:
    from typing import Sequence

    from crescent.internal.app_command import AppCommandMeta
    from crescent.internal.includable import Includable
    from crescent.typedefs import HookCallbackT

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

    def child(self, includable: Includable[AppCommandMeta]) -> Includable[AppCommandMeta]:
        includable.metadata.group = self

        add_hooks(self, includable)

        return includable


@define
class SubGroup:
    name: str
    parent: Group
    description: str | None = None
    hooks: list[HookCallbackT] | None = None
    after_hooks: list[HookCallbackT] | None = None

    def child(self, includable: Includable[AppCommandMeta]) -> Includable[AppCommandMeta]:
        includable.metadata.group = self.parent
        includable.metadata.sub_group = self

        add_hooks(self, includable)
        add_hooks(self.parent, includable)

        return includable
