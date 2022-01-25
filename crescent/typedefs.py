from __future__ import annotations

from typing import Any, Awaitable, Callable, Sequence, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from .context import Context

__all__: Sequence[str] = ("CommandCallback",)

CommandCallback = Callable[..., Awaitable[Any]]


class ClassCommandProto(Protocol):
    async def callback(self, ctx: Context) -> Any:
        ...
