from __future__ import annotations

from typing import TYPE_CHECKING, Any, Awaitable, Callable, Protocol, Sequence

if TYPE_CHECKING:
    from .context import Context

__all__: Sequence[str] = ("CommandCallback",)

CommandCallback = Callable[..., Awaitable[Any]]


class ClassCommandProto(Protocol):
    async def callback(self, ctx: Context) -> Any:
        ...
