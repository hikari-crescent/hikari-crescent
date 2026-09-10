"""Option classes for class commands.

Options are declared as class attributes on a class command. The attribute name
is converted to kebab-case for the option name unless `name` is given.

```python
import crescent
from crescent import options

@client.include
@crescent.command(name="repeat")
class Repeat:
    word = options.String("The word to repeat")
    times = options.Integer("How many times", default=1, min_value=1, max_value=10)

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.respond(" ".join(self.word for i in range(self.times))
```
"""

from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import TYPE_CHECKING, ClassVar, Generic, Never, TypeVar, overload

import hikari

from crescent.locale import LocaleBuilder, str_or_build_locale
from crescent.mentionable import Mentionable as CrescentMentionable
from crescent.utils import kebab_case

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Sequence
    from typing import Self

    from crescent.typedefs import AutocompleteCallbackT

__all__ = (
    "Attachment",
    "Boolean",
    "Channel",
    "ChoiceOption",
    "ClassCommandOption",
    "Float",
    "Integer",
    "Mentionable",
    "NumericOption",
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
    """Base class for all option types."""

    description: str | LocaleBuilder
    """The description for the option."""
    _: KW_ONLY
    name: hikari.UndefinedOr[str | LocaleBuilder] = hikari.UNDEFINED
    """The user-facing option name. Defaults to the attribute name in kebab-case."""
    default: hikari.UndefinedOr[D] = hikari.UNDEFINED
    """The value to use when the user does not fill out the option.

    Setting this makes the option optional. Default values bypass converters."""
    converter: Callable[[T], C_co] | None = None
    """A callable that takes the value returned by Discord and converts it.

    Supports async, sync, and sync->Awaitable callables. Exceptions raised are
    aggregated together into a [`ConverterExceptions`][crescent.exceptions.ConverterExceptions].
    """

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
        name, name_localizations = str_or_build_locale(
            kebab_case(field) if self.name is hikari.UNDEFINED else self.name,
        )
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
class ChoiceOption(ClassCommandOption[ChoiceT, C_co, D], Generic[ChoiceT, C_co, D]):
    """Base class for options that support choices and autocomplete."""

    choices: Sequence[tuple[str | LocaleBuilder, ChoiceT] | hikari.CommandChoice] | None = None
    """A fixed set of values the user must pick from.

    Must be a sequence of `(name, value)` tuples or
    [`hikari.CommandChoice`][hikari.commands.CommandChoice]s. Discord allows up to 25 options.

    Mutually exclusive with autocomplete."""
    autocomplete: AutocompleteCallbackT[ChoiceT] | None = None
    """A callable that provides suggestions for options as the user types.

    Takes an [`AutocompleteContext`][crescent.context.AutocompleteContext] and
    the focused `hikari.AutocompleteInteractionOption`, and returns a sequence of
    `(name, value)` tuples.

    ```python
    async def suggest(
        ctx: crescent.AutocompleteContext, option: hikari.AutocompleteInteractionOption
    ) -> list[tuple[str, str]]:
        return [("Some Option", "1234")]

    class Command:
        result = options.String("Pick a value", autocomplete=suggest)
    ```

    Mutually exclusive with choices."""

    def _gen_option(self, field: str) -> hikari.CommandOption:
        option = super(ChoiceOption, self)._gen_option(field)
        option.choices = _build_choices(self.choices) if self.choices else None
        option.autocomplete = self.autocomplete is not None
        return option


@dataclass(frozen=True, slots=True, kw_only=True)
class NumericOption(ChoiceOption[NumericT, C_co, D], Generic[NumericT, C_co, D]):
    """Base class for number options."""

    min_value: NumericT | None = None
    """The minimum allowed value."""
    max_value: NumericT | None = None
    """The maximum allowed value."""

    def _gen_option(self, field: str) -> hikari.CommandOption:
        option = super(NumericOption, self)._gen_option(field)
        option.min_value = self.min_value
        option.max_value = self.max_value
        return option


@dataclass(frozen=True, slots=True, kw_only=True)
class String(ChoiceOption[str, C_co, D], Generic[C_co, D]):
    """A string option."""

    _type: ClassVar[hikari.OptionType] = hikari.OptionType.STRING
    min_length: int | None = None
    """The minimum number of characters."""
    max_length: int | None = None
    """The maximum number of characters."""

    def _gen_option(self, field: str) -> hikari.CommandOption:
        option = super(String, self)._gen_option(field)
        option.min_length = self.min_length
        option.max_length = self.max_length
        return option


@dataclass(frozen=True, slots=True)
class Integer(NumericOption[int, C_co, D], Generic[C_co, D]):
    """An integer option."""

    _type: ClassVar[hikari.OptionType] = hikari.OptionType.INTEGER


@dataclass(frozen=True, slots=True)
class Float(NumericOption[float, C_co, D], Generic[C_co, D]):
    """A float option."""

    _type: ClassVar[hikari.OptionType] = hikari.OptionType.FLOAT


@dataclass(frozen=True, slots=True)
class Boolean(ClassCommandOption[bool, C_co, D], Generic[C_co, D]):
    """A boolean option."""

    _type: ClassVar[hikari.OptionType] = hikari.OptionType.BOOLEAN


@dataclass(frozen=True, slots=True, kw_only=True)
class Channel(ClassCommandOption[hikari.InteractionChannel, C_co, D], Generic[C_co, D]):
    """A channel option.

    Value: [`hikari.InteractionChannel`][hikari.interactions.base_interactions.InteractionChannel]
    """

    _type: ClassVar[hikari.OptionType] = hikari.OptionType.CHANNEL
    channel_types: Sequence[hikari.ChannelType] | None = None
    """Which channel types the user may select. Defaults to allowing all."""

    def _gen_option(self, field: str) -> hikari.CommandOption:
        option = super(Channel, self)._gen_option(field)
        option.channel_types = list(self.channel_types) if self.channel_types else None
        return option


@dataclass(frozen=True, slots=True)
class Role(ClassCommandOption[hikari.Role, C_co, D], Generic[C_co, D]):
    """A role option.

    Value: [`hikari.Role`][hikari.guilds.Role]"""

    _type: ClassVar[hikari.OptionType] = hikari.OptionType.ROLE


@dataclass(frozen=True, slots=True)
class User(ClassCommandOption[hikari.User, C_co, D], Generic[C_co, D]):
    """A user option.

    Value: [`hikari.User`][hikari.users.User]"""

    _type: ClassVar[hikari.OptionType] = hikari.OptionType.USER


@dataclass(frozen=True, slots=True)
class Mentionable(ClassCommandOption[CrescentMentionable, C_co, D], Generic[C_co, D]):
    """A mentionable option (i.e., user or role).

    Value: [`Mentionable`][crescent.mentionable.Mentionable]"""

    _type: ClassVar[hikari.OptionType] = hikari.OptionType.MENTIONABLE


@dataclass(frozen=True, slots=True)
class Attachment(ClassCommandOption[hikari.Attachment, C_co, D], Generic[C_co, D]):
    """An attachment option.

    Value: [`hikari.Attachment`][hikari.messages.Attachment]"""

    _type: ClassVar[hikari.OptionType] = hikari.OptionType.ATTACHMENT
