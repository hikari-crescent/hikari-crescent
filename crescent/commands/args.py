from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from attr import define
from hikari import ChannelType, CommandChoice

if TYPE_CHECKING:
    from typing import Sequence, Any
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
    @property
    def payload(self) -> Any:
        """Returns the data for this object"""
        ...


@define
class Description(Arg):
    description: str

    @property
    def payload(self) -> str:
        return self.description


@define
class Name(Arg):
    name: str

    @property
    def payload(self) -> str:
        return self.name


class Choices(Arg):
    def __init__(self, *choices: CommandChoice) -> None:
        self.choices = choices

    @property
    def payload(self) -> Sequence[CommandChoice]:
        return self.choices


class ChannelTypes(Arg):
    def __init__(self, *channel_types: ChannelType) -> None:
        self.channel_types = channel_types

    @property
    def payload(self) -> Sequence[ChannelType]:
        return self.channel_types


@define
class MaxValue(Arg):
    max_value: int

    @property
    def payload(self) -> int:
        return self.max_value


@define
class MinValue(Arg):
    min_value: int

    @property
    def payload(self) -> int:
        return self.min_value


@define
class Autocomplete(Arg):
    callback: AutocompleteCallbackT

    @property
    def payload(self) -> str:
        return self.callback
