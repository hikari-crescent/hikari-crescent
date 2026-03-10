from dataclasses import dataclass, replace
from typing import Any, Awaitable, Callable, Generic, Sequence, TypeVar, cast, overload
from typing_extensions import Never, Self

from hikari import (
    UNDEFINED,
    Attachment,
    ChannelType,
    CommandChoice,
    CommandOption,
    InteractionChannel,
    OptionType,
    PartialChannel,
    Role,
    UndefinedOr,
    User,
)

from crescent.commands.options import build_choices
from crescent.locale import LocaleBuilder, str_or_build_locale
from crescent.mentionable import Mentionable
from crescent.typedefs import AutocompleteCallbackT


# fmt: off
class _Marker: ...
class _StrMarker(_Marker): ...
class _BoolMarker(_Marker): ...
class _IntMarker(_Marker): ...
class _FloatMarker(_Marker): ...
class _ChannelMarker(_Marker): ...
class _RoleMarker(_Marker): ...
class _UserMarker(_Marker): ...
class _MentionableMarker(_Marker): ...
class _AttachmentMarker(_Marker): ...
# fmt: on


MarkT = TypeVar("MarkT", bound=_Marker)
InT = TypeVar("InT")
ConverterT = TypeVar("ConverterT")
DefaultT = TypeVar("DefaultT")
ChannelTypeT = TypeVar("ChannelTypeT", bound=PartialChannel)
T = TypeVar("T")


@dataclass(slots=True)
class ClassCommandOption(Generic[MarkT, InT, ConverterT, DefaultT]):
    _type: OptionType
    _description: str | LocaleBuilder
    _name: UndefinedOr[str | LocaleBuilder] = UNDEFINED
    _default: UndefinedOr[DefaultT] = UNDEFINED
    _choices: Sequence[CommandChoice] | None = None
    _channel_types: Sequence[ChannelType] | None = None
    _min_value: int | float | None = None
    _max_value: int | float | None = None
    _min_length: int | None = None
    _max_length: int | None = None
    _autocomplete: AutocompleteCallbackT[Any] | None = None
    _converter: Callable[[InT], ConverterT | Awaitable[ConverterT]] | None = None

    def name(self, name: str | LocaleBuilder) -> Self:
        return replace(self, _name=name)

    def default(self, default: T) -> "ClassCommandOption[MarkT, InT, ConverterT, T]":
        return replace(
            cast("ClassCommandOption[MarkT, InT, ConverterT, T]", self),
            _default=default,
        )

    def convert(
        self, converter: Callable[[InT], T]
    ) -> "ClassCommandOption[MarkT, InT, T, DefaultT]":
        return replace(
            cast("ClassCommandOption[MarkT, InT, T, DefaultT]", self),
            _converter=converter,
        )

    def channel_types(
        self: "ClassCommandOption[_ChannelMarker, InT, ConverterT, DefaultT]",
        types: Sequence[ChannelType],
    ) -> "ClassCommandOption[_ChannelMarker, InT, ConverterT, DefaultT]":
        return replace(self, _channel_types=types)

    @overload
    def autocomplete(
        self: "ClassCommandOption[_IntMarker, InT, ConverterT, DefaultT]",
        autocomplete: AutocompleteCallbackT[int],
    ) -> "ClassCommandOption[_IntMarker, InT, ConverterT, DefaultT]": ...
    @overload
    def autocomplete(
        self: "ClassCommandOption[_FloatMarker, InT, ConverterT, DefaultT]",
        autocomplete: AutocompleteCallbackT[float],
    ) -> "ClassCommandOption[_FloatMarker, InT, ConverterT, DefaultT]": ...
    @overload
    def autocomplete(
        self: "ClassCommandOption[_StrMarker, InT, ConverterT, DefaultT]",
        autocomplete: AutocompleteCallbackT[str],
    ) -> "ClassCommandOption[_StrMarker, InT, ConverterT, DefaultT]": ...

    def autocomplete(self, autocomplete: AutocompleteCallbackT[Any]) -> Any:
        return replace(self, _autocomplete=autocomplete)

    @overload
    def choices(
        self: "ClassCommandOption[_IntMarker, InT, ConverterT, DefaultT]",
        choices: Sequence[tuple[str | LocaleBuilder, int] | CommandChoice],
    ) -> "ClassCommandOption[_IntMarker, InT, ConverterT, DefaultT]": ...
    @overload
    def choices(
        self: "ClassCommandOption[_FloatMarker, InT, ConverterT, DefaultT]",
        choices: Sequence[tuple[str | LocaleBuilder, float] | CommandChoice],
    ) -> "ClassCommandOption[_FloatMarker, InT, ConverterT, DefaultT]": ...
    @overload
    def choices(
        self: "ClassCommandOption[_StrMarker, InT, ConverterT, DefaultT]",
        choices: Sequence[tuple[str | LocaleBuilder, str] | CommandChoice],
    ) -> "ClassCommandOption[_StrMarker, InT, ConverterT, DefaultT]": ...

    def choices(
        self, choices: Sequence[tuple[str | LocaleBuilder, int | str | float] | CommandChoice]
    ) -> Any:
        return replace(self, _choices=build_choices(choices))

    def min_value(
        self: "ClassCommandOption[_IntMarker, InT, ConverterT, DefaultT]",
        value: int,
    ) -> "ClassCommandOption[_IntMarker, InT, ConverterT, DefaultT]":
        return replace(self, _min_value=value)

    def max_value(
        self: "ClassCommandOption[_IntMarker, InT, ConverterT, DefaultT]",
        value: int,
    ) -> "ClassCommandOption[_IntMarker, InT, ConverterT, DefaultT]":
        return replace(self, _max_value=value)

    def min_length(
        self: "ClassCommandOption[_StrMarker, InT, ConverterT, DefaultT]",
        value: int,
    ) -> "ClassCommandOption[_StrMarker, InT, ConverterT, DefaultT]":
        return replace(self, _min_value=value)

    def max_length(
        self: "ClassCommandOption[_StrMarker, InT, ConverterT, DefaultT]",
        value: int,
    ) -> "ClassCommandOption[_StrMarker, InT, ConverterT, DefaultT]":
        return replace(self, _max_value=value)

    @overload
    def __get__(self, inst: None, cls: Any) -> Self: ...

    @overload
    def __get__(
        self: "ClassCommandOption[MarkT, InT, Never, Never]", inst: object, cls: Any
    ) -> InT: ...
    @overload
    def __get__(
        self: "ClassCommandOption[MarkT, InT, ConverterT, Never]", inst: object, cls: Any
    ) -> ConverterT: ...
    @overload
    def __get__(
        self: "ClassCommandOption[MarkT, InT, Never, DefaultT]", inst: object, cls: Any
    ) -> InT | DefaultT: ...
    @overload
    def __get__(
        self: "ClassCommandOption[MarkT, InT, ConverterT, DefaultT]", inst: object, cls: Any
    ) -> ConverterT | DefaultT: ...

    def __get__(self, inst: Any | None, cls: Any) -> Any:
        if inst is None:
            return self

        # we should never reach this point
        raise NotImplementedError

    def _gen_option(self, name: str) -> CommandOption:
        name, name_localizations = str_or_build_locale(self._name or name)
        description, description_localizations = str_or_build_locale(self._description)

        return CommandOption(
            type=self._type,
            name=name,
            name_localizations=name_localizations,
            description=description,
            description_localizations=description_localizations,
            is_required=self.default is UNDEFINED,
            choices=self._choices,
            channel_types=self._channel_types,
            min_value=self._min_value,
            max_value=self._max_value,
            min_length=self._min_length,
            max_length=self._max_length,
            autocomplete=self._autocomplete is not None,
        )


@dataclass(slots=True, frozen=True)
class _OptionBuilder(Generic[MarkT, InT]):
    _type: OptionType

    def __call__(
        self, description: str | LocaleBuilder
    ) -> ClassCommandOption[MarkT, InT, Never, Never]:
        return ClassCommandOption(_description=description, _type=self._type)


string: _OptionBuilder[_StrMarker, str] = _OptionBuilder(OptionType.STRING)
boolean: _OptionBuilder[_BoolMarker, bool] = _OptionBuilder(OptionType.BOOLEAN)
number: _OptionBuilder[_IntMarker, int] = _OptionBuilder(OptionType.INTEGER)
floating: _OptionBuilder[_FloatMarker, float] = _OptionBuilder(OptionType.FLOAT)
channel: _OptionBuilder[_ChannelMarker, InteractionChannel] = _OptionBuilder(OptionType.CHANNEL)
role: _OptionBuilder[_RoleMarker, Role] = _OptionBuilder(OptionType.ROLE)
user: _OptionBuilder[_UserMarker, User] = _OptionBuilder(OptionType.USER)
mentionable: _OptionBuilder[_MentionableMarker, Mentionable] = _OptionBuilder(
    OptionType.MENTIONABLE
)
attachment: _OptionBuilder[_AttachmentMarker, Attachment] = _OptionBuilder(OptionType.ATTACHMENT)
