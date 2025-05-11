from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Iterable, TypeVar

from hikari import (
    UNDEFINED,
    ApplicationContextType,
    CommandOption,
    PartialCommand,
    Permissions,
    SlashCommand,
    Snowflakeish,
)
from hikari.api import EntityFactory

from crescent.locale import LocaleBuilder, str_or_build_locale
from crescent.utils import add_hooks

if TYPE_CHECKING:
    from typing import Any, Sequence, Type

    from hikari import CommandType, Snowflake, UndefinedOr, UndefinedType

    from crescent.commands.groups import Group, SubGroup
    from crescent.internal.includable import Includable
    from crescent.typedefs import AutocompleteCallbackT, CommandCallbackT, CommandHookCallbackT

    Self = TypeVar("Self")


@dataclass(frozen=True)
class Unique:
    name: str
    type: CommandType
    guild_id: Snowflakeish | None
    group: str | None
    sub_group: str | None

    @classmethod
    def from_meta_struct(cls: Type[Unique], command: Includable[AppCommandMeta]) -> Unique:
        return cls(
            name=str_or_build_locale(command.metadata.app_command.name)[0],
            type=command.metadata.app_command.type,
            guild_id=command.metadata.app_command.guild_id,
            group=str_or_build_locale(command.metadata.group.name)[0]
            if command.metadata.group
            else None,
            sub_group=str_or_build_locale(command.metadata.sub_group.name)[0]
            if command.metadata.sub_group
            else None,
        )

    @classmethod
    def from_app_command_meta(cls: Type[Unique], command: AppCommandMeta) -> Unique:
        return cls(
            name=str_or_build_locale(command.app_command.name)[0],
            type=command.app_command.type,
            guild_id=command.app_command.guild_id,
            group=str_or_build_locale(command.group.name)[0] if command.group else None,
            sub_group=str_or_build_locale(command.sub_group.name)[0]
            if command.sub_group
            else None,
        )


__all__: Sequence[str] = ("AppCommandMeta", "AppCommand")


@dataclass
class AppCommand:
    """Local representation of an Application Command"""

    type: CommandType
    name: str | LocaleBuilder
    guild_id: Snowflakeish | None

    description: str | LocaleBuilder | None = None
    options: Sequence[CommandOption] | None = None
    default_member_permissions: UndefinedType | int | Permissions = UNDEFINED
    context_types: UndefinedOr[Iterable[ApplicationContextType]] = UNDEFINED
    nsfw: bool | None = None
    id: UndefinedOr[Snowflake] = UNDEFINED

    def eq_partial_command(self, other: PartialCommand) -> bool:
        name, name_localizations = str_or_build_locale(self.name)

        if isinstance(other, SlashCommand):
            if self.description:
                description, description_localizations = str_or_build_locale(self.description)
            else:
                description = None
                description_localizations = None

            if any(
                (
                    description != other.description,
                    (self.options or None) != (other.options or None),
                    description_localizations != other.description_localizations,
                )
            ):
                return False

        context_types: set[ApplicationContextType] = (
            set(self.context_types) if self.context_types is not UNDEFINED else set()
        )

        return all(
            (
                self.type == other.type,
                name == other.name,
                name_localizations == other.name_localizations,
                context_types == set(other.context_types),
                self.build_default_member_perms() or 0 == other.default_member_permissions,
            )
        )

    def build_default_member_perms(self) -> Permissions | None:
        if self.default_member_permissions is UNDEFINED:
            return None
        return Permissions(self.default_member_permissions)

    def build(self, encoder: EntityFactory) -> dict[str, Any]:
        name, name_localizations = str_or_build_locale(self.name)

        out: dict[str, Any] = {
            "name": name,
            "name_localizations": name_localizations,
            "type": self.type,
        }

        if self.description:
            description, description_localizations = str_or_build_locale(self.description)
            out["description"] = description
            out["description_localizations"] = description_localizations
        if self.options:
            out["options"] = [encoder.serialize_command_option(option) for option in self.options]

        if self.nsfw is not None:
            out["nsfw"] = self.nsfw

        if (perms := self.build_default_member_perms()) is not None:
            out["default_member_permissions"] = str(perms.value)

        if self.context_types:
            out["contexts"] = [c.value for c in self.context_types]

        return out


@dataclass
class AppCommandMeta:
    app_command: AppCommand
    owner: Any
    """The function or class that was used to create the command"""
    callback: CommandCallbackT
    autocomplete: dict[str, AutocompleteCallbackT[Any]] = field(default_factory=dict)  # pyright: ignore[reportUnknownVariableType]
    group: Group | None = None
    sub_group: SubGroup | None = None
    hooks: list[CommandHookCallbackT] = field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]
    after_hooks: list[CommandHookCallbackT] = field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]

    def add_hooks(
        self, hooks: Sequence[CommandHookCallbackT], prepend: bool = False, *, after: bool
    ) -> None:
        add_hooks(self.hooks, self.after_hooks, hooks, prepend=prepend, after=after)

    @property
    def unique(self) -> Unique:
        return Unique(
            str_or_build_locale(self.app_command.name)[0],
            self.app_command.type,
            self.app_command.guild_id,
            str_or_build_locale(self.group.name)[0] if self.group else None,
            str_or_build_locale(self.sub_group.name)[0] if self.sub_group else None,
        )
