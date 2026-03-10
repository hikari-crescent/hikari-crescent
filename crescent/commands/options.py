"""Builder-based option declarations for class commands."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast, overload

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
from typing_extensions import Never, Self

from crescent.locale import LocaleBuilder, str_or_build_locale

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Sequence

    from crescent.mentionable import Mentionable
    from crescent.typedefs import AutocompleteCallbackT

__all__ = (
    "AttachmentMarker",
    "BoolMarker",
    "ChannelMarker",
    "ClassCommandOption",
    "FloatMarker",
    "IntMarker",
    "Marker",
    "MentionableMarker",
    "RoleMarker",
    "StrMarker",
    "UserMarker",
    "attachment",
    "boolean",
    "channel",
    "floating",
    "mentionable",
    "number",
    "role",
    "string",
    "user",
)


# fmt: off
class Marker: ...
class StrMarker(Marker): ...
class BoolMarker(Marker): ...
class IntMarker(Marker): ...
class FloatMarker(Marker): ...
class ChannelMarker(Marker): ...
class RoleMarker(Marker): ...
class UserMarker(Marker): ...
class MentionableMarker(Marker): ...
class AttachmentMarker(Marker): ...
# fmt: on


MarkT = TypeVar("MarkT", bound=Marker)
InT = TypeVar("InT")
ConverterT = TypeVar("ConverterT")
DefaultT = TypeVar("DefaultT")
ChannelTypeT = TypeVar("ChannelTypeT", bound=PartialChannel)
T = TypeVar("T")


def _build_choices(
    choices: Sequence[tuple[str | LocaleBuilder, str | int | float] | CommandChoice],
) -> list[CommandChoice]:
    result: list[CommandChoice] = []
    for choice in choices:
        if isinstance(choice, CommandChoice):
            result.append(choice)
            continue

        name, value = choice
        name, name_localizations = str_or_build_locale(name)
        result.append(CommandChoice(name=name, name_localizations=name_localizations, value=value))

    return result


@dataclass(slots=True)
class ClassCommandOption(Generic[MarkT, InT, ConverterT, DefaultT]):
    """A declarative option definition used by class-based slash commands.

    Instances of this class are usually created through the builder objects
    exported by this module, such as [`string`][crescent.commands.options.string]
    or [`channel`][crescent.commands.options.channel].
    """

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
        """Set the Discord-facing name for this option."""
        return replace(self, _name=name)

    def default(self, default: T) -> ClassCommandOption[MarkT, InT, ConverterT, T]:
        """Set a default value, making this option optional."""
        return replace(
            cast("ClassCommandOption[MarkT, InT, ConverterT, T]", self),
            _default=default,
        )

    def convert(
        self, converter: Callable[[InT], T | Awaitable[T]]
    ) -> ClassCommandOption[MarkT, InT, T, DefaultT]:
        """Convert the raw option value before assigning it to the command instance."""
        return replace(
            cast("ClassCommandOption[MarkT, InT, T, DefaultT]", self),
            _converter=converter,
        )

    def channel_types(
        self: ClassCommandOption[ChannelMarker, InT, ConverterT, DefaultT],
        types: Sequence[ChannelType],
    ) -> ClassCommandOption[ChannelMarker, InT, ConverterT, DefaultT]:
        """Restrict which Discord channel types may be selected for this option."""
        return replace(self, _channel_types=types)

    @overload
    def autocomplete(
        self: ClassCommandOption[IntMarker, InT, ConverterT, DefaultT],
        autocomplete: AutocompleteCallbackT[int],
    ) -> ClassCommandOption[IntMarker, InT, ConverterT, DefaultT]: ...
    @overload
    def autocomplete(
        self: ClassCommandOption[FloatMarker, InT, ConverterT, DefaultT],
        autocomplete: AutocompleteCallbackT[float],
    ) -> ClassCommandOption[FloatMarker, InT, ConverterT, DefaultT]: ...
    @overload
    def autocomplete(
        self: ClassCommandOption[StrMarker, InT, ConverterT, DefaultT],
        autocomplete: AutocompleteCallbackT[str],
    ) -> ClassCommandOption[StrMarker, InT, ConverterT, DefaultT]: ...

    def autocomplete(self, autocomplete: AutocompleteCallbackT[Any]) -> Any:
        """Attach an autocomplete callback to this option."""
        return replace(self, _autocomplete=autocomplete)

    @overload
    def choices(
        self: ClassCommandOption[IntMarker, InT, ConverterT, DefaultT],
        choices: Sequence[tuple[str | LocaleBuilder, int] | CommandChoice],
    ) -> ClassCommandOption[IntMarker, InT, ConverterT, DefaultT]: ...
    @overload
    def choices(
        self: ClassCommandOption[FloatMarker, InT, ConverterT, DefaultT],
        choices: Sequence[tuple[str | LocaleBuilder, float] | CommandChoice],
    ) -> ClassCommandOption[FloatMarker, InT, ConverterT, DefaultT]: ...
    @overload
    def choices(
        self: ClassCommandOption[StrMarker, InT, ConverterT, DefaultT],
        choices: Sequence[tuple[str | LocaleBuilder, str] | CommandChoice],
    ) -> ClassCommandOption[StrMarker, InT, ConverterT, DefaultT]: ...

    def choices(
        self, choices: Sequence[tuple[str | LocaleBuilder, int | str | float] | CommandChoice]
    ) -> Any:
        """Set the fixed choices users may select for this option."""
        return replace(self, _choices=_build_choices(choices))

    @overload
    def min_value(
        self: ClassCommandOption[IntMarker, InT, ConverterT, DefaultT],
        value: int,
    ) -> ClassCommandOption[IntMarker, InT, ConverterT, DefaultT]: ...

    @overload
    def min_value(
        self: ClassCommandOption[FloatMarker, InT, ConverterT, DefaultT],
        value: float,
    ) -> ClassCommandOption[FloatMarker, InT, ConverterT, DefaultT]: ...

    def min_value(self, value: int | float) -> Any:
        """Set the inclusive minimum numeric value for this option."""
        return replace(self, _min_value=value)

    @overload
    def max_value(
        self: ClassCommandOption[IntMarker, InT, ConverterT, DefaultT],
        value: int,
    ) -> ClassCommandOption[IntMarker, InT, ConverterT, DefaultT]: ...

    @overload
    def max_value(
        self: ClassCommandOption[FloatMarker, InT, ConverterT, DefaultT],
        value: float,
    ) -> ClassCommandOption[FloatMarker, InT, ConverterT, DefaultT]: ...

    def max_value(self, value: int | float) -> Any:
        """Set the inclusive maximum numeric value for this option."""
        return replace(self, _max_value=value)

    def min_length(
        self: ClassCommandOption[StrMarker, InT, ConverterT, DefaultT],
        value: int,
    ) -> ClassCommandOption[StrMarker, InT, ConverterT, DefaultT]:
        """Set the inclusive minimum string length for this option."""
        return replace(self, _min_length=value)

    def max_length(
        self: ClassCommandOption[StrMarker, InT, ConverterT, DefaultT],
        value: int,
    ) -> ClassCommandOption[StrMarker, InT, ConverterT, DefaultT]:
        """Set the inclusive maximum string length for this option."""
        return replace(self, _max_length=value)

    @overload
    def __get__(self, inst: None, cls: Any) -> Self: ...

    @overload
    def __get__(
        self: ClassCommandOption[MarkT, InT, Never, Never], inst: object, cls: Any
    ) -> InT: ...
    @overload
    def __get__(
        self: ClassCommandOption[MarkT, InT, ConverterT, Never], inst: object, cls: Any
    ) -> ConverterT: ...
    @overload
    def __get__(
        self: ClassCommandOption[MarkT, InT, Never, DefaultT], inst: object, cls: Any
    ) -> InT | DefaultT: ...
    @overload
    def __get__(
        self: ClassCommandOption[MarkT, InT, ConverterT, DefaultT], inst: object, cls: Any
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
            is_required=self._default is UNDEFINED,
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
    """Internal callable builder for a specific Discord option type."""

    _type: OptionType

    def __call__(
        self, description: str | LocaleBuilder
    ) -> ClassCommandOption[MarkT, InT, Never, Never]:
        """Create an option declaration with the provided description."""
        return ClassCommandOption(_description=description, _type=self._type)


string: _OptionBuilder[StrMarker, str] = _OptionBuilder(OptionType.STRING)
boolean: _OptionBuilder[BoolMarker, bool] = _OptionBuilder(OptionType.BOOLEAN)
number: _OptionBuilder[IntMarker, int] = _OptionBuilder(OptionType.INTEGER)
floating: _OptionBuilder[FloatMarker, float] = _OptionBuilder(OptionType.FLOAT)
channel: _OptionBuilder[ChannelMarker, InteractionChannel] = _OptionBuilder(OptionType.CHANNEL)
role: _OptionBuilder[RoleMarker, Role] = _OptionBuilder(OptionType.ROLE)
user: _OptionBuilder[UserMarker, User] = _OptionBuilder(OptionType.USER)
mentionable: _OptionBuilder[MentionableMarker, Mentionable] = _OptionBuilder(
    OptionType.MENTIONABLE
)
attachment: _OptionBuilder[AttachmentMarker, Attachment] = _OptionBuilder(OptionType.ATTACHMENT)
