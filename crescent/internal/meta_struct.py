from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from attr import define, field

from crescent.utils.options import unwrap

if TYPE_CHECKING:
    from typing import Any, Awaitable, Callable, List, Optional, Sequence

    from crescent.bot import Bot

T = TypeVar("T", bound="Callable[..., Awaitable[Any]]")
U = TypeVar("U")

__all__: Sequence[str] = ("MetaStruct",)


@define
class MetaStruct(Generic[T, U]):

    callback: T
    metadata: U

    manager: Optional[Any] = None
    _app: Optional[Bot] = None

    app_set_hooks: List[Callable[[MetaStruct[T, U]], None]] = field(factory=list)

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
