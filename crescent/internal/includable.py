from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from attr import define, field

from crescent.utils.options import unwrap

if TYPE_CHECKING:
    from typing import Any, Callable, Sequence

    from crescent.client import Client

T = TypeVar("T")

__all__: Sequence[str] = ("Includable",)


@define
class Includable(Generic[T]):

    metadata: T

    manager: Any | None = None
    _client: Client | None = None

    client_set_hooks: list[Callable[[Includable[T]], None]] = field(factory=list)
    plugin_unload_hooks: list[Callable[[Includable[T]], None]] = field(factory=list)

    @property
    def client(self) -> Client:
        return unwrap(self._client)

    @client.setter
    def client(self, client: Client) -> None:
        self._client = client

        for hook in self.client_set_hooks:
            hook(self)

    def register_to_client(self, client: Client) -> None:
        self.client = client
