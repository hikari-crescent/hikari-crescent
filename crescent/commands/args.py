from abc import ABC
from typing import Any
from attr import define


class Arg(ABC):
    @property
    def payload() -> Any:
        """Returns the data for this object"""
        ...


@define
class Description:
    description: str

    @property
    def payload(self) -> str:
        return self.description


@define
class Name:
    name: str

    @property
    def payload(self) -> str:
        return self.name
