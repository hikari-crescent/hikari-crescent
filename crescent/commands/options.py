from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence, Tuple, Type, TypeVar, Union, overload

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

__all__ = (
    "OPTIONS_TYPE_MAP",
    "get_channel_types",
    "option",
    "ClassCommandOption",
)

_VALID_TYPES = Union[str, bool, int, float, PartialChannel, Role, User, Mentionable]
OPTIONS_TYPE_MAP: Dict[Type[_VALID_TYPES], OptionType] = {
    str: OptionType.STRING,
    bool: OptionType.BOOLEAN,
    int: OptionType.INTEGER,
    float: OptionType.FLOAT,
    PartialChannel: OptionType.CHANNEL,
    Role: OptionType.ROLE,
    User: OptionType.USER,
    Mentionable: OptionType.MENTIONABLE,
}
_VALID_CHANNEL_TYPES = Union[
    GuildTextChannel,
    DMChannel,
    GroupDMChannel,
    GuildVoiceChannel,
    GuildCategory,
    GuildNewsChannel,
    GuildStoreChannel,
    GuildStageChannel,
]
_CHANNEL_TYPE_MAP: Dict[Type[_VALID_CHANNEL_TYPES], ChannelType] = {
    GuildTextChannel: ChannelType.GUILD_TEXT,
    DMChannel: ChannelType.DM,
    GuildVoiceChannel: ChannelType.GUILD_VOICE,
    GroupDMChannel: ChannelType.GROUP_DM,
    GuildCategory: ChannelType.GUILD_CATEGORY,
    GuildNewsChannel: ChannelType.GUILD_NEWS,
    GuildStoreChannel: ChannelType.GUILD_STORE,
    GuildStageChannel: ChannelType.GUILD_STAGE,
}


def get_channel_types(*channels: Type[PartialChannel]) -> set[ChannelType] | None:
    types: set[ChannelType] = set()
    for k, v in _CHANNEL_TYPE_MAP.items():
        if isinstance(k, channels):
            types.add(v)

    return types


@dataclass
class ClassCommandOption:
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
            name=name,
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
) -> InteractionChannel:
    ...


@overload
def option(
    option_type: Union[Type[PartialChannel], Sequence[PartialChannel]],
    description: str = ...,
    *,
    default: DEFAULT,
) -> Union[InteractionChannel, DEFAULT]:
    ...


@overload
def option(
    option_type: Type[USER_ROLE_MENTION_OR_BOOL],
    description: str = ...,
) -> USER_ROLE_MENTION_OR_BOOL:
    ...


@overload
def option(
    option_type: Type[USER_ROLE_MENTION_OR_BOOL],
    description: str = ...,
    *,
    default: DEFAULT,
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
) -> Union[INT_OR_FLOAT, DEFAULT]:
    ...


@overload
def option(
    option_type: Type[str],
    description: str = ...,
    *,
    choices: Optional[Sequence[Tuple[str, str]]] = ...,
    min_value: Optional[str] = ...,
    max_value: Optional[str] = ...,
) -> str:
    ...


@overload
def option(
    option_type: Type[str],
    description: str = ...,
    *,
    default: DEFAULT,
    choices: Optional[Sequence[Tuple[str, str]]] = ...,
    min_value: Optional[str] = ...,
    max_value: Optional[str] = ...,
) -> Union[str, DEFAULT]:
    ...


def option(  # type: ignore
    option_type: Union[Type[_VALID_TYPES], Sequence[Type[_VALID_CHANNEL_TYPES]]],
    description: str = "\u200B",
    *,
    default: UndefinedOr[Any] = UNDEFINED,
    choices: Sequence[Tuple[str, Union[str, int, float]]] | None = None,
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
) -> Any:
    if isinstance(option_type, type) and issubclass(option_type, PartialChannel):
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
    )
