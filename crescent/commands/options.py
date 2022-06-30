from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, Sequence, TypeVar, Union, cast, overload

from hikari import (
    UNDEFINED,
    Attachment,
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

OPTIONS_TYPE_MAP: dict[type[OptionTypesT], OptionType] = {
    str: OptionType.STRING,
    bool: OptionType.BOOLEAN,
    int: OptionType.INTEGER,
    float: OptionType.FLOAT,
    PartialChannel: OptionType.CHANNEL,
    Role: OptionType.ROLE,
    User: OptionType.USER,
    Mentionable: OptionType.MENTIONABLE,
    Attachment: OptionType.ATTACHMENT,
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
CHANNEL_TYPE_MAP: dict[type[VALID_CHANNEL_TYPES], ChannelType] = {
    GuildTextChannel: ChannelType.GUILD_TEXT,
    DMChannel: ChannelType.DM,
    GuildVoiceChannel: ChannelType.GUILD_VOICE,
    GroupDMChannel: ChannelType.GROUP_DM,
    GuildCategory: ChannelType.GUILD_CATEGORY,
    GuildNewsChannel: ChannelType.GUILD_NEWS,
    GuildStageChannel: ChannelType.GUILD_STAGE,
}


def get_channel_types(*channels: type[PartialChannel]) -> set[ChannelType]:
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
    name: str | None
    type: OptionType
    description: str
    default: UndefinedNoneOr[Any]
    choices: Sequence[CommandChoice] | None
    channel_types: Sequence[ChannelType] | None
    min_value: int | float | None
    max_value: int | float | None
    autocomplete: AutocompleteCallbackT | None

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
    def __get__(self, inst: object, cls: Any) -> T:
        ...

    def __get__(self, inst: Any | None, cls: Any) -> Any:
        if inst is None:
            return self

        # we should never reach this point
        raise NotImplementedError


DEFAULT = TypeVar("DEFAULT")

# mypy doesn't understand abstract classes, so this is necessary and hence # pyright: ignore
# (github issues 4717, 5374)
USER = TypeVar("USER", bound="type[User]")
ROLE = TypeVar("ROLE", bound="type[Role]")
ATTACHMENT = TypeVar("ATTACHMENT", bound="type[Attachment]")


@overload
def option(
    option_type: type[PartialChannel] | Sequence[type[PartialChannel]],
    description: str = ...,
    *,
    name: str | None = ...,
) -> ClassCommandOption[InteractionChannel]:
    ...


@overload
def option(
    option_type: type[PartialChannel] | Sequence[type[PartialChannel]],
    description: str = ...,
    *,
    default: DEFAULT,
    name: str | None = ...,
) -> ClassCommandOption[InteractionChannel | DEFAULT]:
    ...


# fmt: off
@overload
def option(
    option_type: USER,  # pyright: ignore
    description: str = ...,
    *, name: str | None = ...,
) -> ClassCommandOption[User]:
    ...
# fmt: on


@overload
def option(
    option_type: USER,  # pyright: ignore
    description: str = ...,
    *,
    default: DEFAULT,
    name: str | None = ...,
) -> ClassCommandOption[User | DEFAULT]:
    ...


# fmt: off
@overload
def option(
    option_type: ROLE,  # pyright: ignore
    description: str = ...,
    *,
    name: str | None = ...,
) -> ClassCommandOption[Role]:
    ...
# fmt: on


@overload
def option(
    option_type: ROLE,  # pyright: ignore
    description: str = ...,
    *,
    default: DEFAULT,
    name: str | None = ...,
) -> ClassCommandOption[Role | DEFAULT]:
    ...


# fmt: off
@overload
def option(
    option_type: ATTACHMENT,  # pyright: ignore
    description: str = ...,
    *,
    name: str | None = ...,
) -> ClassCommandOption[Attachment]:
    ...
# fmt: on


@overload
def option(
    option_type: ATTACHMENT,  # pyright: ignore
    description: str = ...,
    *,
    default: DEFAULT,
    name: str | None = ...,
) -> ClassCommandOption[Attachment | DEFAULT]:
    ...


@overload
def option(
    option_type: type[Mentionable], description: str = ..., *, name: str | None = ...
) -> ClassCommandOption[Mentionable]:
    ...


@overload
def option(
    option_type: type[Mentionable],
    description: str = ...,
    *,
    default: DEFAULT,
    name: str | None = ...,
) -> ClassCommandOption[Mentionable | DEFAULT]:
    ...


@overload
def option(  # type: ignore
    option_type: type[bool], description: str = ..., *, name: str | None = ...
) -> ClassCommandOption[bool]:
    ...


@overload
def option(  # type: ignore
    option_type: type[bool], description: str = ..., *, default: DEFAULT, name: str | None = ...
) -> ClassCommandOption[bool | DEFAULT]:
    ...


@overload
def option(
    option_type: type[int],
    description: str = ...,
    *,
    choices: Sequence[tuple[str, int]] | None = ...,
    autocomplete: AutocompleteCallbackT | None = ...,
    min_value: int | None = ...,
    max_value: int | None = ...,
    name: str | None = ...,
) -> ClassCommandOption[int]:
    ...


@overload
def option(
    option_type: type[int],
    description: str = ...,
    *,
    default: DEFAULT,
    choices: Sequence[tuple[str, int]] | None = ...,
    autocomplete: AutocompleteCallbackT | None = ...,
    min_value: int | None = ...,
    max_value: int | None = ...,
    name: str | None = ...,
) -> ClassCommandOption[int | DEFAULT]:
    ...


@overload
def option(
    option_type: type[float],
    description: str = ...,
    *,
    choices: Sequence[tuple[str, float]] | None = ...,
    autocomplete: AutocompleteCallbackT | None = ...,
    min_value: float | None = ...,
    max_value: float | None = ...,
    name: str | None = ...,
) -> ClassCommandOption[float]:
    ...


@overload
def option(
    option_type: type[float],
    description: str = ...,
    *,
    default: DEFAULT,
    choices: Sequence[tuple[str, float]] | None = ...,
    autocomplete: AutocompleteCallbackT | None = ...,
    min_value: float | None = ...,
    max_value: float | None = ...,
    name: str | None = ...,
) -> ClassCommandOption[float | DEFAULT]:
    ...


@overload
def option(
    option_type: type[str],
    description: str = ...,
    *,
    choices: Sequence[tuple[str, str]] | None = ...,
    autocomplete: AutocompleteCallbackT | None = ...,
    name: str | None = ...,
) -> ClassCommandOption[str]:
    ...


@overload
def option(
    option_type: type[str],
    description: str = ...,
    *,
    default: DEFAULT,
    choices: Sequence[tuple[str, str]] | None = ...,
    autocomplete: AutocompleteCallbackT | None = ...,
    name: str | None = ...,
) -> ClassCommandOption[str | DEFAULT]:
    ...


def option(
    option_type: type[OptionTypesT] | Sequence[type[PartialChannel]],
    description: str = "No Description",
    *,
    default: UndefinedOr[Any] = UNDEFINED,
    choices: Sequence[tuple[str, str | int | float]] | None = None,
    min_value: int | float | None = None,
    max_value: int | float | None = None,
    name: str | None = None,
    autocomplete: AutocompleteCallbackT | None = None,
) -> ClassCommandOption[Any]:

    _option_type: type[OptionTypesT]
    if (
        isinstance(option_type, type)
        and issubclass(option_type, PartialChannel)
        and option_type is not PartialChannel
    ):
        option_type = cast("type[VALID_CHANNEL_TYPES]", option_type)
        channel_types = get_channel_types(option_type)
        _option_type = PartialChannel
    elif isinstance(option_type, Sequence):
        channel_types = get_channel_types(*option_type)
        _option_type = PartialChannel
    else:
        _option_type = option_type
        channel_types = None

    return ClassCommandOption(
        type=OPTIONS_TYPE_MAP[_option_type],
        description=description,
        default=default,
        choices=[CommandChoice(name=n, value=v) for n, v in choices] if choices else None,
        channel_types=list(channel_types) if channel_types else None,
        min_value=min_value,
        max_value=max_value,
        name=name,
        autocomplete=autocomplete,
    )
