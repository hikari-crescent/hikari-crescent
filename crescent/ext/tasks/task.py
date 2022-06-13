from __future__ import annotations

from abc import ABC, abstractmethod
from asyncio import ensure_future, get_event_loop
from typing import Any, Awaitable, Callable, Sequence, TypeVar

from crescent.bot import Bot
from crescent.internal.meta_struct import MetaStruct

TaskCallbackT = Callable[[], Awaitable[None]]

__all__: Sequence[str] = ("TaskCallbackT", "Task")


class Task(ABC):
    def __init__(self, callback: TaskCallbackT) -> None:
        self.event_loop = get_event_loop()
        self.callback = callback
        self.running = True
        self.app: Bot | None = None

    def start(self) -> None:
        ensure_future(self._start_inner())

    async def _start_inner(self) -> None:
        assert self.app is not None

        await self.app.started.wait()

        self.call_next()

    def stop(self) -> None:
        self.running = False

    def call_async(self) -> None:
        if not self.running:
            return
        ensure_future(self.callback())
        self.call_next()

    def call_next(self) -> None:
        self.event_loop.call_later(self.time_to_next(), self.call_async)

    @abstractmethod
    def time_to_next(self) -> float:
        ...


_TaskType = TypeVar("_TaskType", bound=Task)


def _on_app_set(self: MetaStruct[TaskCallbackT, _TaskType]) -> None:
    self.metadata.app = self.app
    self.metadata.start()


def _unload(self: MetaStruct[TaskCallbackT, _TaskType]) -> None:
    self.metadata.stop()


def link_task(meta: MetaStruct[Any, _TaskType]) -> None:
    meta.app_set_hooks.append(_on_app_set)
    meta.plugin_unload_hooks.append(_unload)
