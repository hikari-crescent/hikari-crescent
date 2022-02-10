from __future__ import annotations

from dataclasses import dataclass
from inspect import isclass
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

from hikari import (
    UNDEFINED,
    ChannelType,
    CommandChoice,
    CommandOption,
    DMChannel,
    GroupDMChannel,
    GuildCategory,
    GuildNewsChannel,
    GuildStageChannel,
    GuildStoreChannel,
    GuildTextChannel,
    GuildVoiceChannel,
    InteractionChannel,
    OptionType,
    PartialChannel,
    Role,
    UndefinedNoneOr,
    UndefinedOr,
    User,
)

from crescent.mentionable import Mentionable

if TYPE_CHECKING:
    from crescent.typedefs import OptionTypesT

__all__ = (
    "OPTIONS_TYPE_MAP",
    "VALID_CHANNEL_TYPES",
    "CHANNEL_TYPE_MAP",
    "get_channel_types",
    "option",
    "ClassCommandOption",
)

OPTIONS_TYPE_MAP: Dict[Type[OptionTypesT], OptionType] = {
    str: OptionType.STRING,
    bool: OptionType.BOOLEAN,
    int: OptionType.INTEGER,
    float: OptionType.FLOAT,
    PartialChannel: OptionType.CHANNEL,
    Role: OptionType.ROLE,
    User: OptionType.USER,
    Mentionable: OptionType.MENTIONABLE,
}
VALID_CHANNEL_TYPES = Union[
    GuildTextChannel,
    DMChannel,
    GroupDMChannel,
    GuildVoiceChannel,
    GuildCategory,
    GuildNewsChannel,
    GuildStoreChannel,
    GuildStageChannel,
]
CHANNEL_TYPE_MAP: Dict[Type[VALID_CHANNEL_TYPES], ChannelType] = {
    GuildTextChannel: ChannelType.GUILD_TEXT,
    DMChannel: ChannelType.DM,
    GuildVoiceChannel: ChannelType.GUILD_VOICE,
    GroupDMChannel: ChannelType.GROUP_DM,
    GuildCategory: ChannelType.GUILD_CATEGORY,
    GuildNewsChannel: ChannelType.GUILD_NEWS,
    GuildStoreChannel: ChannelType.GUILD_STORE,
    GuildStageChannel: ChannelType.GUILD_STAGE,
}


def get_channel_types(*channels: Type[PartialChannel]) -> set[ChannelType]:
    if len(channels) == 1 and channels[0] is PartialChannel:
        return set()

    types: set[ChannelType] = set()
    for k, v in CHANNEL_TYPE_MAP.items():
        if issubclass(k, channels):
            types.add(v)

    return types


@dataclass
class ClassCommandOption:
    name: Optional[str]
    type: OptionType
    description: str
    default: UndefinedNoneOr[Any]
    choices: Optional[Sequence[CommandChoice]]
    channel_types: Optional[Sequence[ChannelType]]
    min_value: Optional[Union[int, float]]
    max_value: Optional[Union[int, float]]

    def _gen_option(self, name: str) -> CommandOption:
        return CommandOption(
            type=self.type,
            name=self.name or name,
            description=self.description,
            is_required=self.default is UNDEFINED,
            choices=self.choices,
            channel_types=self.channel_types,
            min_value=self.min_value,
            max_value=self.max_value,
        )


DEFAULT = TypeVar("DEFAULT")
INT_OR_FLOAT = TypeVar("INT_OR_FLOAT", int, float)
USER_ROLE_MENTION_OR_BOOL = TypeVar("USER_ROLE_MENTION_OR_BOOL", User, Role, Mentionable, bool)


@overload
def option(
    option_type: Union[Type[PartialChannel], Sequence[PartialChannel]],
    description: str = ...,
    *,
    name: Optional[str] = ...,
) -> InteractionChannel:
    ...


@overload
def option(
    option_type: Union[Type[PartialChannel], Sequence[PartialChannel]],
    description: str = ...,
    *,
    default: DEFAULT,
    name: Optional[str] = ...,
) -> Union[InteractionChannel, DEFAULT]:
    ...


@overload
def option(
    option_type: Type[USER_ROLE_MENTION_OR_BOOL],
    description: str = ...,
    *,
    name: Optional[str] = ...,
) -> USER_ROLE_MENTION_OR_BOOL:
    ...


@overload
def option(
    option_type: Type[USER_ROLE_MENTION_OR_BOOL],
    description: str = ...,
    *,
    default: DEFAULT,
    name: Optional[str] = ...,
) -> Union[USER_ROLE_MENTION_OR_BOOL, DEFAULT]:
    ...


@overload
def option(
    option_type: Type[INT_OR_FLOAT],
    description: str = ...,
    *,
    choices: Optional[Sequence[Tuple[str, INT_OR_FLOAT]]] = ...,
    min_value: Optional[INT_OR_FLOAT] = ...,
    max_value: Optional[INT_OR_FLOAT] = ...,
    name: Optional[str] = ...,
) -> INT_OR_FLOAT:
    ...


@overload
def option(
    option_type: Type[INT_OR_FLOAT],
    description: str = ...,
    *,
    default: DEFAULT,
    choices: Optional[Sequence[Tuple[str, INT_OR_FLOAT]]] = ...,
    min_value: Optional[INT_OR_FLOAT] = ...,
    max_value: Optional[INT_OR_FLOAT] = ...,
    name: Optional[str] = ...,
) -> Union[INT_OR_FLOAT, DEFAULT]:
    ...


@overload
def option(
    option_type: Type[str],
    description: str = ...,
    *,
    choices: Optional[Sequence[Tuple[str, str]]] = ...,
    name: Optional[str] = ...,
) -> str:
    ...


@overload
def option(
    option_type: Type[str],
    description: str = ...,
    *,
    default: DEFAULT,
    choices: Optional[Sequence[Tuple[str, str]]] = ...,
    name: Optional[str] = ...,
) -> Union[str, DEFAULT]:
    ...


def option(  # type: ignore
    option_type: Union[Type[OptionTypesT], Sequence[Type[VALID_CHANNEL_TYPES]]],
    description: str = "\u200B",
    *,
    default: UndefinedOr[Any] = UNDEFINED,
    choices: Sequence[Tuple[str, Union[str, int, float]]] | None = None,
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
    name: Optional[str] = None,
) -> Any:
    if (
        isclass(option_type)
        and issubclass(option_type, PartialChannel)
        and option_type is not PartialChannel
    ):
        option_type = cast(Type[VALID_CHANNEL_TYPES], option_type)
        channel_types = get_channel_types(option_type)
        option_type = PartialChannel
    elif isinstance(option_type, Sequence):
        channel_types = get_channel_types(*option_type)
        option_type = PartialChannel
    else:
        channel_types = None

    return ClassCommandOption(
        type=OPTIONS_TYPE_MAP[option_type],
        description=description,
        default=default,
        choices=[CommandChoice(name=n, value=v) for n, v in choices] if choices else None,
        channel_types=list(channel_types) if channel_types else None,
        min_value=min_value,
        max_value=max_value,
        name=name,
    )
