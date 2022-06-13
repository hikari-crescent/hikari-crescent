from __future__ import annotations

from abc import ABC, abstractmethod
from asyncio import TimerHandle, ensure_future, get_event_loop
from typing import Any, Awaitable, Callable, Sequence, TypeVar

from crescent.bot import Bot
from crescent.internal.meta_struct import MetaStruct

TaskCallbackT = Callable[[], Awaitable[None]]

__all__: Sequence[str] = ("TaskCallbackT", "Task")


class Task(ABC):
    def __init__(self, callback: TaskCallbackT) -> None:
        self.event_loop = get_event_loop()
        self.callback = callback
        self.timer_handle: TimerHandle | None = None
        self.app: Bot | None = None

    def start(self) -> None:
        ensure_future(self._start_inner())

    async def _start_inner(self) -> None:
        assert self.app is not None

        await self.app.started.wait()

        self._call_next()

    def stop(self) -> None:
        if self.timer_handle:
            self.timer_handle.cancel()

    @property
    def running(self) -> bool:
        if not self.timer_handle:
            return False
        return not self.timer_handle.cancelled()

    def _call_async(self) -> None:
        ensure_future(self.callback())
        self._call_next()

    def _call_next(self) -> None:
        self.timer_handle = self.event_loop.call_later(self.time_to_next(), self._call_async)

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
