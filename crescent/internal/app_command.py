from __future__ import annotations

from typing import TYPE_CHECKING

from attr import define, field
from hikari import UNDEFINED, CommandOption, Snowflakeish
from hikari.api import CommandBuilder, EntityFactory
from hikari.internal.data_binding import JSONObject

if TYPE_CHECKING:
    from typing import Any, Dict, List, Optional, Sequence, Type

    from hikari import CommandType, Snowflake, UndefinedNoneOr, UndefinedOr

    from crescent.commands.groups import Group, SubGroup
    from crescent.internal.meta_struct import MetaStruct
    from crescent.typedefs import AutocompleteCallbackT, CommandCallbackT, HookCallbackT


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
    guild_id: Optional[Snowflakeish]
    default_permission: UndefinedOr[bool]

    description: Optional[str] = None
    options: Optional[Sequence[CommandOption]] = None
    id: UndefinedOr[Snowflake] = UNDEFINED

    __eq__props: Sequence[str] = ("type", "name", "description", "guild_id", "options")

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
        return all((self.guild_id == o.guild_id, self.name == o.name, self.type == o.type))

    def build(self, encoder: EntityFactory) -> JSONObject:
        out: Dict[str, Any] = {"name": self.name, "type": self.type}

        if self.description:
            out["description"] = self.description
        if self.options:
            out["options"] = [encoder.serialize_command_option(option) for option in self.options]
        if self.default_permission:
            out["default_permission"] = self.default_permission

        return out

    def set_default_permission(self, state: UndefinedOr[bool]) -> AppCommand:
        self.default_permission = state
        return self

    def set_id(self, _id: UndefinedOr[Snowflakeish]) -> AppCommand:
        if isinstance(_id, int):
            _id = Snowflake(_id)
        self.id = _id
        return self


@define
class AppCommandMeta:
    app: AppCommand
    autocomplete: Dict[str, AutocompleteCallbackT] = field(factory=dict)
    group: Optional[Group] = None
    sub_group: Optional[SubGroup] = None
    deprecated: bool = False
    hooks: List[HookCallbackT] = field(factory=list)
    after_hooks: List[HookCallbackT] = field(factory=list)

    @property
    def unique(self) -> Unique:
        return Unique(
            self.app.name,
            self.app.type,
            self.app.guild_id,
            self.group.name if self.group else None,
            self.sub_group.name if self.sub_group else None,
        )
