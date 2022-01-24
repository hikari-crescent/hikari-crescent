from abc import ABC
from typing import Any, Sequence

from attr import define
from hikari import ChannelType, CommandChoice

__all__: Sequence[str] = (
    "Description",
    "Name",
    "Choices",
    "ChannelTypes",
    "MaxValue",
    "MinValue",
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


@define
class Choices(Arg):
    choices: Sequence[CommandChoice]

    @property
    def payload(self) -> Sequence[CommandChoice]:
        return self.choices


@define
class ChannelTypes(Arg):
    channel_types: Sequence[ChannelType]

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
