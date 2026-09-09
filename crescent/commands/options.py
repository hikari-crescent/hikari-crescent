"""Typed option descriptors for class commands."""

from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import TYPE_CHECKING, ClassVar, Generic, Never, TypeVar, overload

import hikari

from crescent.locale import LocaleBuilder, str_or_build_locale
from crescent.mentionable import Mentionable as CrescentMentionable

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Sequence
    from typing import Self

    from crescent.typedefs import AutocompleteCallbackT

__all__ = (
    "Attachment",
    "Boolean",
    "Channel",
    "ClassCommandOption",
    "Float",
    "Integer",
    "Mentionable",
    "Role",
    "String",
    "User",
)


T = TypeVar("T")
C_co = TypeVar("C_co", default=Never, covariant=True)
D = TypeVar("D", default=Never)
ChoiceT = TypeVar("ChoiceT", str, int, float)
NumericT = TypeVar("NumericT", int, float)


def _build_choices(
    choices: Sequence[tuple[str | LocaleBuilder, str | int | float] | hikari.CommandChoice],
) -> list[hikari.CommandChoice]:
    result: list[hikari.CommandChoice] = []
    for choice in choices:
        if isinstance(choice, hikari.CommandChoice):
            result.append(choice)
            continue

        name, value = choice
        name, name_localizations = str_or_build_locale(name)
        result.append(
            hikari.CommandChoice(name=name, name_localizations=name_localizations, value=value),
        )

    return result


@dataclass(frozen=True, slots=True)
class ClassCommandOption(Generic[T, C_co, D]):
    """The base option class for slash commands.

    Don't use this directly; use one of the subclasses:
    - [`String`][crescent.commands.options.String]
    - [`Integer`][crescent.commands.options.Integer]
    - [`Float`][crescent.commands.options.Float]
    - [`Boolean`][crescent.commands.options.Boolean]
    - [`Channel`][crescent.commands.options.Channel]
    - [`Role`][crescent.commands.options.Role]
    - [`User`][crescent.commands.options.User]
    - [`Mentionable`][crescent.commands.options.Mentionable]
    - [`Attachment`][crescent.commands.options.Attachment]
    """

    description: str | LocaleBuilder
    _: KW_ONLY
    name: hikari.UndefinedOr[str | LocaleBuilder] = hikari.UNDEFINED
    default: hikari.UndefinedOr[D] = hikari.UNDEFINED
    converter: Callable[[T], C_co] | None = None

    _type: ClassVar[hikari.OptionType]

    @overload
    def __get__(self, inst: None, cls: type[object]) -> Self: ...

    @overload
    def __get__(
        self: ClassCommandOption[T, Never, D],
        inst: object,
        cls: type[object],
    ) -> T | D: ...

    @overload
    def __get__[A](
        self: ClassCommandOption[T, Awaitable[A], D],
        inst: object,
        cls: type[object],
    ) -> A | D: ...

    @overload
    def __get__(
        self: ClassCommandOption[T, C_co, D],
        inst: object,
        cls: type[object],
    ) -> C_co | D: ...

    def __get__(self, inst: object | None, cls: type[object]) -> object:
        if inst is None:
            return self

        raise NotImplementedError

    def _gen_option(self, field: str) -> hikari.CommandOption:
        name, name_localizations = str_or_build_locale(self.name or field)
        description, description_localizations = str_or_build_locale(self.description)

        return hikari.CommandOption(
            type=self._type,
            name=name,
            name_localizations=name_localizations,
            description=description,
            description_localizations=description_localizations,
            is_required=self.default is hikari.UNDEFINED,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class _ChoiceOption(ClassCommandOption[ChoiceT, C_co, D], Generic[ChoiceT, C_co, D]):
    choices: Sequence[tuple[str | LocaleBuilder, ChoiceT] | hikari.CommandChoice] | None = None
    autocomplete: AutocompleteCallbackT[ChoiceT] | None = None

    def _gen_option(self, field: str) -> hikari.CommandOption:
        option = super(_ChoiceOption, self)._gen_option(field)
        option.choices = _build_choices(self.choices) if self.choices is not None else None
        option.autocomplete = self.autocomplete is not None
        return option


@dataclass(frozen=True, slots=True, kw_only=True)
class _NumericOption(_ChoiceOption[NumericT, C_co, D], Generic[NumericT, C_co, D]):
    min_value: NumericT | None = None
    max_value: NumericT | None = None

    def _gen_option(self, field: str) -> hikari.CommandOption:
        option = super(_NumericOption, self)._gen_option(field)
        option.min_value = self.min_value
        option.max_value = self.max_value
        return option


@dataclass(frozen=True, slots=True, kw_only=True)
class String(_ChoiceOption[str, C_co, D], Generic[C_co, D]):
    """A string option."""

    _type: ClassVar[hikari.OptionType] = hikari.OptionType.STRING
    min_length: int | None = None
    max_length: int | None = None

    def _gen_option(self, field: str) -> hikari.CommandOption:
        option = super(String, self)._gen_option(field)
        option.min_length = self.min_length
        option.max_length = self.max_length
        return option


@dataclass(frozen=True, slots=True)
class Integer(_NumericOption[int, C_co, D], Generic[C_co, D]):
    """An integer option."""

    _type: ClassVar[hikari.OptionType] = hikari.OptionType.INTEGER


@dataclass(frozen=True, slots=True)
class Float(_NumericOption[float, C_co, D], Generic[C_co, D]):
    """A float option."""

    _type: ClassVar[hikari.OptionType] = hikari.OptionType.FLOAT


@dataclass(frozen=True, slots=True)
class Boolean(ClassCommandOption[bool, C_co, D], Generic[C_co, D]):
    """A boolean option."""

    _type: ClassVar[hikari.OptionType] = hikari.OptionType.BOOLEAN


@dataclass(frozen=True, slots=True, kw_only=True)
class Channel(ClassCommandOption[hikari.InteractionChannel, C_co, D], Generic[C_co, D]):
    """A channel option."""

    _type: ClassVar[hikari.OptionType] = hikari.OptionType.CHANNEL
    channel_types: Sequence[hikari.ChannelType] | None = None

    def _gen_option(self, field: str) -> hikari.CommandOption:
        option = super(Channel, self)._gen_option(field)
        option.channel_types = self.channel_types
        return option


@dataclass(frozen=True, slots=True)
class Role(ClassCommandOption[hikari.Role, C_co, D], Generic[C_co, D]):
    """A role option."""

    _type: ClassVar[hikari.OptionType] = hikari.OptionType.ROLE


@dataclass(frozen=True, slots=True)
class User(ClassCommandOption[hikari.User, C_co, D], Generic[C_co, D]):
    """A user option."""

    _type: ClassVar[hikari.OptionType] = hikari.OptionType.USER


@dataclass(frozen=True, slots=True)
class Mentionable(ClassCommandOption[CrescentMentionable, C_co, D], Generic[C_co, D]):
    """A mentionable option (i.e., user or role)."""

    _type: ClassVar[hikari.OptionType] = hikari.OptionType.MENTIONABLE


@dataclass(frozen=True, slots=True)
class Attachment(ClassCommandOption[hikari.Attachment, C_co, D], Generic[C_co, D]):
    """An attachment option."""

    _type: ClassVar[hikari.OptionType] = hikari.OptionType.ATTACHMENT
