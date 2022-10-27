from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from attr import define, field

from crescent.utils.options import unwrap

if TYPE_CHECKING:
    from typing import Any, Callable, Sequence

    from crescent.bot import Mixin

T = TypeVar("T")

__all__: Sequence[str] = ("Includable",)


@define
class Includable(Generic[T]):

    metadata: T

    manager: Any | None = None
    _app: Mixin | None = None

    app_set_hooks: list[Callable[[Includable[T]], None]] = field(factory=list)
    plugin_unload_hooks: list[Callable[[Includable[T]], None]] = field(factory=list)

    @property
    def app(self) -> Mixin:
        return unwrap(self._app)

    @app.setter
    def app(self, app: Mixin) -> None:
        self._app = app

        for hook in self.app_set_hooks:
            hook(self)

    def register_to_app(self, app: Mixin) -> None:
        self.app = app
