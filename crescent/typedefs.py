from __future__ import annotations

from typing import Any, Awaitable, Callable, Protocol, Sequence

from crescent.context import Context
from crescent.commands.hooks import HookResult


__all__: Sequence[str] = (
    "CommandCallback",
    "HookCallbackT",
    "ClassCommandProto",
)

CommandCallback = Callable[..., Awaitable[Any]]
HookCallbackT = Callable[[Context], Awaitable[HookResult]]


class ClassCommandProto(Protocol):
    async def callback(self, ctx: Context) -> Any:
        ...
