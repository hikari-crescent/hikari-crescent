from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from attr import define, field

from crescent.utils.options import unwrap

if TYPE_CHECKING:
    from typing import Any, Callable, Sequence

    from crescent.bot import Bot

T = TypeVar("T")

__all__: Sequence[str] = ("Includable",)


@define
class Includable(Generic[T]):

    metadata: T

    manager: Any | None = None
    _app: Bot | None = None

    app_set_hooks: list[Callable[[Includable[T]], None]] = field(factory=list)
    plugin_unload_hooks: list[Callable[[Includable[T]], None]] = field(factory=list)

    @property
    def app(self) -> Bot:
        return unwrap(self._app)

    @app.setter
    def app(self, app: Bot) -> None:
        self._app = app

        for hook in self.app_set_hooks:
            hook(self)

    def register_to_app(self, app: Bot) -> None:
        self.app = app
