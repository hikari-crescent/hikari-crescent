from __future__ import annotations

from dataclasses import dataclass
from inspect import isclass
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
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
    from crescent.typedefs import AutocompleteCallbackT, OptionTypesT

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
    GuildStageChannel,
]
CHANNEL_TYPE_MAP: Dict[Type[VALID_CHANNEL_TYPES], ChannelType] = {
    GuildTextChannel: ChannelType.GUILD_TEXT,
    DMChannel: ChannelType.DM,
    GuildVoiceChannel: ChannelType.GUILD_VOICE,
    GroupDMChannel: ChannelType.GROUP_DM,
    GuildCategory: ChannelType.GUILD_CATEGORY,
    GuildNewsChannel: ChannelType.GUILD_NEWS,
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


T = TypeVar("T")
Self = TypeVar("Self")


@dataclass
class ClassCommandOption(Generic[T]):
    name: Optional[str]
    type: OptionType
    description: str
    default: UndefinedNoneOr[Any]
    choices: Optional[Sequence[CommandChoice]]
    channel_types: Optional[Sequence[ChannelType]]
    min_value: Optional[Union[int, float]]
    max_value: Optional[Union[int, float]]
    autocomplete: Optional[AutocompleteCallbackT]

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
            autocomplete=bool(self.autocomplete),
        )

    @overload
    def __get__(self: Self, inst: None, cls: Any) -> Self:
        ...

    @overload
    def __get__(self: Self, inst: object, cls: Any) -> T:
        ...

    def __get__(self, inst: Any | None, cls: Any) -> Any:
        if inst is None:
            return self

        # we should never reach this point
        raise NotImplementedError


DEFAULT = TypeVar("DEFAULT")
USER = TypeVar("USER", bound=Type[User])
ROLE = TypeVar("ROLE", bound=Type[Role])


@overload
def option(
    option_type: Union[Type[PartialChannel], Sequence[Type[PartialChannel]]],
    description: str = ...,
    *,
    name: Optional[str] = ...,
) -> ClassCommandOption[InteractionChannel]:
    ...


@overload
def option(
    option_type: Union[Type[PartialChannel], Sequence[Type[PartialChannel]]],
    description: str = ...,
    *,
    default: DEFAULT,
    name: Optional[str] = ...,
) -> ClassCommandOption[Union[InteractionChannel, DEFAULT]]:
    ...


@overload
def option(
    option_type: USER, description: str = ..., *, name: Optional[str] = ...
) -> ClassCommandOption[User]:
    ...


@overload
def option(
    option_type: USER, description: str = ..., *, default: DEFAULT, name: Optional[str] = ...
) -> ClassCommandOption[Union[User, DEFAULT]]:
    ...


@overload
def option(
    option_type: ROLE, description: str = ..., *, name: Optional[str] = ...
) -> ClassCommandOption[Role]:
    ...


@overload
def option(
    option_type: ROLE, description: str = ..., *, default: DEFAULT, name: Optional[str] = ...
) -> ClassCommandOption[Union[Role, DEFAULT]]:
    ...


@overload
def option(
    option_type: Type[Mentionable], description: str = ..., *, name: Optional[str] = ...
) -> ClassCommandOption[Mentionable]:
    ...


@overload
def option(
    option_type: Type[Mentionable],
    description: str = ...,
    *,
    default: DEFAULT,
    name: Optional[str] = ...,
) -> ClassCommandOption[Union[Mentionable, DEFAULT]]:
    ...


@overload
def option(  # type: ignore
    option_type: Type[bool], description: str = ..., *, name: Optional[str] = ...
) -> ClassCommandOption[bool]:
    ...


@overload
def option(  # type: ignore
    option_type: Type[bool], description: str = ..., *, default: DEFAULT, name: Optional[str] = ...
) -> ClassCommandOption[Union[bool, DEFAULT]]:
    ...


@overload
def option(
    option_type: Type[int],
    description: str = ...,
    *,
    choices: Optional[Sequence[Tuple[str, int]]] = ...,
    autocomplete: Optional[AutocompleteCallbackT] = ...,
    min_value: Optional[int] = ...,
    max_value: Optional[int] = ...,
    name: Optional[str] = ...,
) -> ClassCommandOption[int]:
    ...


@overload
def option(
    option_type: Type[int],
    description: str = ...,
    *,
    default: DEFAULT,
    choices: Optional[Sequence[Tuple[str, int]]] = ...,
    autocomplete: Optional[AutocompleteCallbackT] = ...,
    min_value: Optional[int] = ...,
    max_value: Optional[int] = ...,
    name: Optional[str] = ...,
) -> ClassCommandOption[Union[int, DEFAULT]]:
    ...


@overload
def option(
    option_type: Type[float],
    description: str = ...,
    *,
    choices: Optional[Sequence[Tuple[str, float]]] = ...,
    autocomplete: Optional[AutocompleteCallbackT] = ...,
    min_value: Optional[float] = ...,
    max_value: Optional[float] = ...,
    name: Optional[str] = ...,
) -> ClassCommandOption[float]:
    ...


@overload
def option(
    option_type: Type[float],
    description: str = ...,
    *,
    default: DEFAULT,
    choices: Optional[Sequence[Tuple[str, float]]] = ...,
    autocomplete: Optional[AutocompleteCallbackT] = ...,
    min_value: Optional[float] = ...,
    max_value: Optional[float] = ...,
    name: Optional[str] = ...,
) -> ClassCommandOption[Union[float, DEFAULT]]:
    ...


@overload
def option(
    option_type: Type[str],
    description: str = ...,
    *,
    choices: Optional[Sequence[Tuple[str, str]]] = ...,
    autocomplete: Optional[AutocompleteCallbackT] = ...,
    name: Optional[str] = ...,
) -> ClassCommandOption[str]:
    ...


@overload
def option(
    option_type: Type[str],
    description: str = ...,
    *,
    default: DEFAULT,
    choices: Optional[Sequence[Tuple[str, str]]] = ...,
    autocomplete: Optional[AutocompleteCallbackT] = ...,
    name: Optional[str] = ...,
) -> ClassCommandOption[Union[str, DEFAULT]]:
    ...


def option(
    option_type: Union[Type[OptionTypesT], Sequence[Type[PartialChannel]]],
    description: str = "No Description",
    *,
    default: UndefinedOr[Any] = UNDEFINED,
    choices: Sequence[Tuple[str, Union[str, int, float]]] | None = None,
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
    name: Optional[str] = None,
    autocomplete: Optional[AutocompleteCallbackT] = None,
) -> ClassCommandOption[Any]:
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
        autocomplete=autocomplete,
    )
