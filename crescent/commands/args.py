from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic

from hikari import ChannelType, CommandChoice

from crescent.locale import LocaleBuilder
from crescent.typedefs import AutocompleteValueT

if TYPE_CHECKING:
    from typing import Any, Sequence

    from crescent.typedefs import AutocompleteCallbackT

__all__: Sequence[str] = (
    "Description",
    "Name",
    "Choices",
    "ChannelTypes",
    "MaxValue",
    "MinValue",
    "Autocomplete",
)


class Arg(ABC):
    """
    A class to specify argument information when defining a command using a
    function.
    """

    @property
    def _payload(self) -> Any:
        """Returns the data for this object"""
        ...

    def __hash__(self) -> int:
        return super().__hash__() ^ hash(self._payload)


@dataclass(frozen=True)
class Description(Arg):
    """
    Specify the description for functional command syntax.
    """

    description: str | LocaleBuilder

    @property
    def _payload(self) -> str | LocaleBuilder:
        return self.description


@dataclass(frozen=True)
class Name(Arg):
    """
    Specify the name for functional command syntax.
    """

    name: str | LocaleBuilder

    @property
    def _payload(self) -> str | LocaleBuilder:
        return self.name


class Choices(Arg):
    """
    Specify choices for functional command syntax.
    """

    def __init__(self, *choices: CommandChoice) -> None:
        self.choices = choices

    @property
    def _payload(self) -> Sequence[CommandChoice]:
        return self.choices


class ChannelTypes(Arg):
    """
    Specify channel types a command can be used in for functional
    syntax.
    """

    def __init__(self, *channel_types: ChannelType) -> None:
        self.channel_types = channel_types

    @property
    def _payload(self) -> Sequence[ChannelType]:
        return self.channel_types


@dataclass(frozen=True)
class MaxValue(Arg):
    """
    Specify the max value of a number for functional command syntax.
    """

    max_value: int

    @property
    def _payload(self) -> int:
        return self.max_value


@dataclass(frozen=True)
class MinValue(Arg):
    """
    Specify the min value of a number for functional command syntax.
    """

    min_value: int

    @property
    def _payload(self) -> int:
        return self.min_value


@dataclass(frozen=True)
class MinLength(Arg):
    """
    Specify the min length of a string for functional command syntax.
    """

    min_length: int

    @property
    def _payload(self) -> int:
        return self.min_length


@dataclass(frozen=True)
class MaxLength(Arg):
    """
    Specify the max length of a string for functional command syntax.
    """

    max_length: int

    @property
    def _payload(self) -> int:
        return self.max_length


@dataclass(frozen=True)
class Autocomplete(Arg, Generic[AutocompleteValueT]):
    """
    Specify an autocomplete callback for functional command syntax.
    """

    callback: AutocompleteCallbackT[AutocompleteValueT]

    @property
    def _payload(self) -> AutocompleteCallbackT[AutocompleteValueT]:
        return self.callback
