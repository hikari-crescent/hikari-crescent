from abc import ABC
from typing import Any
from attr import define


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
