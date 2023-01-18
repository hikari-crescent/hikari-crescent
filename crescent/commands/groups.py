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
    name: str | LocaleBuilder
    description: str | LocaleBuilder | None = None
    hooks: list[HookCallbackT] | None = None
    after_hooks: list[HookCallbackT] | None = None

    default_member_permissions: UndefinedType | int | Permissions = UNDEFINED
    dm_enabled: bool = True

    def sub_group(
        self,
        name: str | LocaleBuilder,
        description: str | LocaleBuilder | None = None,
        hooks: list[HookCallbackT] | None = None,
        after_hooks: list[HookCallbackT] | None = None,
    ) -> SubGroup:
        return SubGroup(
            name=name, parent=self, description=description, hooks=hooks, after_hooks=after_hooks
        )

    def child(self, includable: Includable[AppCommandMeta]) -> Includable[AppCommandMeta]:
        _check_permissions(includable)

        includable.metadata.group = self

        add_hooks(self, includable)

        return includable


@dataclass
class SubGroup:
    name: str | LocaleBuilder
    parent: Group
    description: str | LocaleBuilder | None = None
    hooks: list[HookCallbackT] | None = None
    after_hooks: list[HookCallbackT] | None = None

    def child(self, includable: Includable[AppCommandMeta]) -> Includable[AppCommandMeta]:
        _check_permissions(includable)

        includable.metadata.group = self.parent
        includable.metadata.sub_group = self

        add_hooks(self, includable)
        add_hooks(self.parent, includable)

        return includable
