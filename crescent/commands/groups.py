from __future__ import annotations

from typing import TYPE_CHECKING

from attr import define

if TYPE_CHECKING:
    from typing import Sequence

    from crescent.internal.app_command import AppCommandMeta
    from crescent.internal.meta_struct import MetaStruct
    from crescent.typedefs import CommandCallback

__all__: Sequence[str] = (
    "Group",
    "SubGroup",
)


@define
class Group:
    name: str

    def sub_group(self, name: str) -> SubGroup:
        return SubGroup(name, self.name)

    def child(
        self, meta: MetaStruct[CommandCallback, AppCommandMeta]
    ) -> MetaStruct[CommandCallback, AppCommandMeta]:
        meta.metadata.group = self.name
        return meta


@define
class SubGroup:
    name: str
    parent: str

    def child(
        self, meta: MetaStruct[CommandCallback, AppCommandMeta]
    ) -> MetaStruct[CommandCallback, AppCommandMeta]:
        meta.metadata.group = self.parent
        meta.metadata.sub_group = self.name
        return meta
