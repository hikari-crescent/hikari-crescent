from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from attr import define, field
from hikari import UNDEFINED, CommandOption, Permissions, Snowflakeish
from hikari.api import CommandBuilder, EntityFactory

from crescent.exceptions import HikariMoment

if TYPE_CHECKING:
    from typing import Any, Sequence, Type

    from hikari import (
        CommandType,
        PartialApplication,
        PartialCommand,
        PartialGuild,
        Snowflake,
        SnowflakeishOr,
        UndefinedNoneOr,
        UndefinedOr,
        UndefinedType,
    )
    from hikari.api.rest import RESTClient

    from crescent.commands.groups import Group, SubGroup
    from crescent.internal.meta_struct import MetaStruct
    from crescent.typedefs import AutocompleteCallbackT, CommandCallbackT, HookCallbackT

    Self = TypeVar("Self")


@define(hash=True)
class Unique:
    name: str
    type: CommandType
    guild_id: UndefinedNoneOr[Snowflakeish]
    group: UndefinedNoneOr[str]
    sub_group: UndefinedNoneOr[str]

    def __attrs_post_init__(self) -> None:
        if self.guild_id is UNDEFINED:
            self.guild_id = None
        if self.group is UNDEFINED:
            self.group = None
        if self.sub_group is UNDEFINED:
            self.sub_group = None

    @classmethod
    def from_meta_struct(
        cls: Type[Unique], command: MetaStruct[CommandCallbackT, AppCommandMeta]
    ) -> Unique:
        return cls(
            name=command.metadata.app.name,
            type=command.metadata.app.type,
            guild_id=command.metadata.app.guild_id,
            group=command.metadata.group.name if command.metadata.group else None,
            sub_group=command.metadata.sub_group.name if command.metadata.sub_group else None,
        )

    @classmethod
    def from_app_command_meta(cls: Type[Unique], command: AppCommandMeta) -> Unique:
        return cls(
            name=command.app.name,
            type=command.app.type,
            guild_id=command.app.guild_id,
            group=command.group.name if command.group else None,
            sub_group=command.sub_group.name if command.sub_group else None,
        )


__all__: Sequence[str] = ("AppCommandMeta", "AppCommand")


@define
class AppCommand(CommandBuilder):
    """Local representation of an Application Command"""

    type: CommandType
    name: str
    guild_id: Snowflakeish | None

    description: str | None = None
    options: Sequence[CommandOption] | None = None
    default_member_permissions: UndefinedType | int | Permissions = UNDEFINED
    is_dm_enabled: bool = True
    id: UndefinedOr[Snowflake] = UNDEFINED

    __eq__props: Sequence[str] = (
        "type",
        "name",
        "description",
        "guild_id",
        "options",
        "default_member_permissions",
        "is_dm_enabled",
    )

    def __eq__(self, __o: object) -> bool:
        """
        Compares properties or class. Any two attributes that are `False` when
        converted to a bool with be considered equal so different methods of
        saying an attribute doesn't exist won't cause issues.
        """
        for prop in self.__eq__props:
            my_attr = getattr(self, prop)
            o_attr = getattr(__o, prop)

            if my_attr != o_attr and (my_attr or o_attr):
                return False

        return True

    def is_same_command(self, o: AppCommand) -> bool:
        return self.guild_id == o.guild_id and self.name == o.name and self.type == o.type

    def build(self, encoder: EntityFactory) -> dict[str, Any]:
        out: dict[str, Any] = {"name": self.name, "type": self.type}

        if self.description:
            out["description"] = self.description
        if self.options:
            out["options"] = [encoder.serialize_command_option(option) for option in self.options]

        if isinstance(self.default_member_permissions, Permissions):
            perms = str(self.default_member_permissions.value)
        elif not self.default_member_permissions:
            perms = None
        else:
            perms = str(self.default_member_permissions)

        out["default_member_permissions"] = perms

        out["dm_permission"] = self.is_dm_enabled

        return out

    def set_id(self, _id: UndefinedOr[Snowflakeish]) -> AppCommand:
        if isinstance(_id, int):
            _id = Snowflake(_id)
        self.id = _id
        return self

    def set_is_dm_enabled(self: Self, state: UndefinedOr[bool], /) -> Self:  # noqa
        raise HikariMoment()

    async def create(  # noqa
        self,
        rest: RESTClient,
        application: SnowflakeishOr[PartialApplication],
        /,
        *,
        guild: UndefinedOr[SnowflakeishOr[PartialGuild]] = UNDEFINED,
    ) -> PartialCommand:
        raise HikariMoment()

    def set_default_member_permissions(  # noqa
        self: Self, default_member_permissions: UndefinedType | int | Permissions, /
    ) -> Self:
        raise HikariMoment()


@define
class AppCommandMeta:
    app: AppCommand
    autocomplete: dict[str, AutocompleteCallbackT] = field(factory=dict)
    group: Group | None = None
    sub_group: SubGroup | None = None
    deprecated: bool = False
    hooks: list[HookCallbackT] = field(factory=list)
    after_hooks: list[HookCallbackT] = field(factory=list)

    @property
    def unique(self) -> Unique:
        return Unique(
            self.app.name,
            self.app.type,
            self.app.guild_id,
            self.group.name if self.group else None,
            self.sub_group.name if self.sub_group else None,
        )
