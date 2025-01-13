from __future__ import annotations

from dataclasses import dataclass, replace
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Generic,
    Sequence,
    TypeVar,
    Union,
    cast,
    overload,
)

from hikari import (
    UNDEFINED,
    Attachment,
    ChannelType,
    CommandChoice,
    CommandOption,
    DMChannel,
    GroupDMChannel,
    GuildCategory,
    GuildForumChannel,
    GuildNewsChannel,
    GuildNewsThread,
    GuildPrivateThread,
    GuildPublicThread,
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

from crescent.locale import LocaleBuilder, str_or_build_locale
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
    GuildNewsThread,
    GuildPublicThread,
    GuildPrivateThread,
    GuildStageChannel,
    GuildForumChannel,
]
CHANNEL_TYPE_MAP: dict[type[VALID_CHANNEL_TYPES], ChannelType] = {
    GuildTextChannel: ChannelType.GUILD_TEXT,
    DMChannel: ChannelType.DM,
    GuildVoiceChannel: ChannelType.GUILD_VOICE,
    GroupDMChannel: ChannelType.GROUP_DM,
    GuildCategory: ChannelType.GUILD_CATEGORY,
    GuildNewsChannel: ChannelType.GUILD_NEWS,
    GuildNewsThread: ChannelType.GUILD_NEWS_THREAD,
    GuildPublicThread: ChannelType.GUILD_PUBLIC_THREAD,
    GuildPrivateThread: ChannelType.GUILD_PRIVATE_THREAD,
    GuildStageChannel: ChannelType.GUILD_STAGE,
    GuildForumChannel: ChannelType.GUILD_FORUM,
}


def build_choices(
    choices: Sequence[tuple[str | LocaleBuilder, str | int | float]],
) -> list[CommandChoice]:
    result: list[CommandChoice] = []
    for name, value in choices:
        name, name_localizations = str_or_build_locale(name)
        result.append(CommandChoice(name=name, name_localizations=name_localizations, value=value))

    return result


def get_channel_types(*channels: type[PartialChannel]) -> set[ChannelType]:
    if len(channels) == 1 and channels[0] is PartialChannel:
        return set()

    types: set[ChannelType] = set()
    for k, v in CHANNEL_TYPE_MAP.items():
        if issubclass(k, channels):  # pyright: ignore
            types.add(v)

    return types


T = TypeVar("T")
In = TypeVar("In")
Out = TypeVar("Out")
Self = TypeVar("Self")


@dataclass
class ClassCommandOption(Generic[In, Out]):
    name: str | LocaleBuilder | None
    type: OptionType
    description: str | LocaleBuilder
    default: UndefinedNoneOr[Any]
    choices: Sequence[CommandChoice] | None
    channel_types: Sequence[ChannelType] | None
    min_value: int | float | None
    max_value: int | float | None
    min_length: int | None
    max_length: int | None
    autocomplete: AutocompleteCallbackT[Any] | None
    converter: Callable[[In], Out | Awaitable[Out]] | None

    def convert(self, converter: Callable[[In], T | Awaitable[T]]) -> ClassCommandOption[In, T]:
        return replace(cast("ClassCommandOption[In, T]", self), converter=converter)

    def _gen_option(self, name: str) -> CommandOption:
        name, name_localizations = str_or_build_locale(self.name or name)
        description, description_localizations = str_or_build_locale(self.description)

        return CommandOption(
            type=self.type,
            name=name,
            name_localizations=name_localizations,
            description=description,
            description_localizations=description_localizations,
            is_required=self.default is UNDEFINED,
            choices=self.choices,
            channel_types=self.channel_types,
            min_value=self.min_value,
            max_value=self.max_value,
            min_length=self.min_length,
            max_length=self.max_length,
            autocomplete=bool(self.autocomplete),
        )

    @overload
    def __get__(self: Self, inst: None, cls: Any) -> Self: ...

    @overload
    def __get__(self, inst: object, cls: Any) -> Out: ...

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
    description: str | LocaleBuilder = ...,
    *,
    name: str | LocaleBuilder | None = ...,
) -> ClassCommandOption[InteractionChannel, InteractionChannel]: ...


@overload
def option(
    option_type: type[PartialChannel] | Sequence[type[PartialChannel]],
    description: str | LocaleBuilder = ...,
    *,
    default: DEFAULT,
    name: str | LocaleBuilder | None = ...,
) -> ClassCommandOption[InteractionChannel | DEFAULT, InteractionChannel | DEFAULT]: ...


# fmt: off
@overload
def option(
    option_type: USER,  # pyright: ignore
    description: str | LocaleBuilder = ...,
    *,
    name: str | LocaleBuilder | None = ...,
) -> ClassCommandOption[User, User]:
    ...
# fmt: on


@overload
def option(
    option_type: USER,  # pyright: ignore
    description: str | LocaleBuilder = ...,
    *,
    default: DEFAULT,
    name: str | LocaleBuilder | None = ...,
) -> ClassCommandOption[User | DEFAULT, User | DEFAULT]: ...


# fmt: off
@overload
def option(
    option_type: ROLE,  # pyright: ignore
    description: str | LocaleBuilder = ...,
    *,
    name: str | LocaleBuilder | None = ...,
) -> ClassCommandOption[Role, Role]:
    ...
# fmt: on


@overload
def option(
    option_type: ROLE,  # pyright: ignore
    description: str | LocaleBuilder = ...,
    *,
    default: DEFAULT,
    name: str | LocaleBuilder | None = ...,
) -> ClassCommandOption[Role | DEFAULT, Role | DEFAULT]: ...


# fmt: off
@overload
def option(
    option_type: ATTACHMENT,  # pyright: ignore
    description: str | LocaleBuilder = ...,
    *,
    name: str | LocaleBuilder | None = ...,
) -> ClassCommandOption[Attachment, Attachment]:
    ...
# fmt: on


@overload
def option(
    option_type: ATTACHMENT,  # pyright: ignore
    description: str | LocaleBuilder = ...,
    *,
    default: DEFAULT,
    name: str | LocaleBuilder | None = ...,
) -> ClassCommandOption[Attachment | DEFAULT, Attachment | DEFAULT]: ...


@overload
def option(
    option_type: type[Mentionable],
    description: str | LocaleBuilder = ...,
    *,
    name: str | LocaleBuilder | None = ...,
) -> ClassCommandOption[Mentionable, Mentionable]: ...


@overload
def option(
    option_type: type[Mentionable],
    description: str | LocaleBuilder = ...,
    *,
    default: DEFAULT,
    name: str | LocaleBuilder | None = ...,
) -> ClassCommandOption[Mentionable | DEFAULT, Mentionable | DEFAULT]: ...


# We have type ignores here because bool and float both inherit from int.
# This makes the typechecker wrongly believe that the overloads overlap.


@overload
def option(  # type: ignore
    option_type: type[bool],
    description: str | LocaleBuilder = ...,
    *,
    name: str | LocaleBuilder | None = ...,
) -> ClassCommandOption[bool, bool]: ...


@overload
def option(  # type: ignore
    option_type: type[bool],
    description: str | LocaleBuilder = ...,
    *,
    default: DEFAULT,
    name: str | LocaleBuilder | None = ...,
) -> ClassCommandOption[bool | DEFAULT, bool | DEFAULT]: ...


@overload
def option(  # type: ignore
    option_type: type[int],
    description: str | LocaleBuilder = ...,
    *,
    choices: Sequence[tuple[str | LocaleBuilder, int]] | None = ...,
    autocomplete: AutocompleteCallbackT[int] | None = ...,
    min_value: int | None = ...,
    max_value: int | None = ...,
    name: str | LocaleBuilder | None = ...,
) -> ClassCommandOption[int, int]: ...


@overload
def option(  # type: ignore
    option_type: type[int],
    description: str | LocaleBuilder = ...,
    *,
    default: DEFAULT,
    choices: Sequence[tuple[str | LocaleBuilder, int]] | None = ...,
    autocomplete: AutocompleteCallbackT[int] | None = ...,
    min_value: int | None = ...,
    max_value: int | None = ...,
    name: str | LocaleBuilder | None = ...,
) -> ClassCommandOption[int | DEFAULT, int | DEFAULT]: ...


@overload
def option(
    option_type: type[float],
    description: str | LocaleBuilder = ...,
    *,
    choices: Sequence[tuple[str | LocaleBuilder, float]] | None = ...,
    autocomplete: AutocompleteCallbackT[float] | None = ...,
    min_value: float | None = ...,
    max_value: float | None = ...,
    name: str | LocaleBuilder | None = ...,
) -> ClassCommandOption[float, float]: ...


@overload
def option(
    option_type: type[float],
    description: str | LocaleBuilder = ...,
    *,
    default: DEFAULT,
    choices: Sequence[tuple[str | LocaleBuilder, float]] | None = ...,
    autocomplete: AutocompleteCallbackT[float] | None = ...,
    min_value: float | None = ...,
    max_value: float | None = ...,
    name: str | LocaleBuilder | None = ...,
) -> ClassCommandOption[float | DEFAULT, float | DEFAULT]: ...


@overload
def option(
    option_type: type[str],
    description: str | LocaleBuilder = ...,
    *,
    min_length: int | None = ...,
    max_length: int | None = ...,
    choices: Sequence[tuple[str | LocaleBuilder, str]] | None = ...,
    autocomplete: AutocompleteCallbackT[str] | None = ...,
    name: str | LocaleBuilder | None = ...,
) -> ClassCommandOption[str, str]: ...


@overload
def option(
    option_type: type[str],
    description: str | LocaleBuilder = ...,
    *,
    default: DEFAULT,
    min_length: int | None = ...,
    max_length: int | None = ...,
    choices: Sequence[tuple[str | LocaleBuilder, str]] | None = ...,
    autocomplete: AutocompleteCallbackT[str] | None = ...,
    name: str | LocaleBuilder | None = ...,
) -> ClassCommandOption[str | DEFAULT, int | DEFAULT]: ...


def option(
    option_type: type[OptionTypesT] | Sequence[type[PartialChannel]],
    description: str | LocaleBuilder = "No Description",
    *,
    name: str | LocaleBuilder | None = None,
    default: UndefinedOr[Any] = UNDEFINED,
    choices: Sequence[tuple[str | LocaleBuilder, str | int | float]] | None = None,
    min_value: int | float | None = None,
    max_value: int | float | None = None,
    min_length: int | None = None,
    max_length: int | None = None,
    autocomplete: AutocompleteCallbackT[Any] | None = None,
) -> ClassCommandOption[Any, Any]:
    """
    An option when declaring a command using class syntax.

    ### Example
    ```python
    @client.include
    @crescent.command(name="say")
    class Say:
        word = crescent.option(str)

        async def callback(self, ctx: crescent.Context):
            await ctx.respond(self.word)
    ```

    Args:
        description:
            The description for this option. Defaults to "No Description".
        name:
            The name to use for this option. By default, the name of the
            property on the option the option is set to will be used for the
            name. In the above example the name would be `word`.
        default:
            The default value for this option. Specifying this will make this
            option optional.
        choices:
            A set of choices a user can pick from for this option. Only available
            for `int`, `str`, and `float` option types.
        min_value:
            The minimum value for a number the user inputs. Only available for
            `int` and `float` option types.
        man_value:
            The maximum value for a number the user inputs. Only available for
            `int` and `float` option types.
        min_length:
            The minimum length for a `str` that the user inputs.
        max_length:
            The maximum length for a `str` that the user inputs.
        autocomplete:
            An autocomplete callback for this option.

            ### Example
            ```python
            async def autocomplete_response(
                ctx: crescent.AutocompleteContext, option: hikari.AutocompleteInteractionOption
            ) -> list[tuple[str, str]]:
                # Return a list of tuples of (option name, option value)
                return [("Some Option", "1234")]

            @client.include
            @crescent.command
            class autocomplete:
                result = crescent.option(str, "Respond to the message", autocomplete=autocomplete_response)

                async def callback(self, ctx: crescent.Context) -> None:
                    await ctx.respond(self.result, ephemeral=True)
            ```
    """  # noqa: E501
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
        choices=build_choices(choices) if choices else None,
        channel_types=list(channel_types) if channel_types else None,
        min_value=min_value,
        max_value=max_value,
        min_length=min_length,
        max_length=max_length,
        name=name,
        autocomplete=autocomplete,
        converter=None,
    )
