from __future__ import annotations

from datetime import timedelta as _timedelta
from typing import Callable, Sequence, overload

from crescent.ext.tasks.task import Task, TaskCallbackT
from crescent.internal import MetaStruct

__all__: Sequence[str] = ("loop", "Loop")


class Loop(Task):
    def __init__(self, callback: TaskCallbackT, delay_seconds: float) -> None:
        self.delay_seconds = delay_seconds
        self.first_loop: bool = True

        super().__init__(callback)

    def _next_iteration(self) -> float:
        """
        Returns 0 if the first loop has not occurred, otherwise return `Loop.delay_seconds`.
        """
        if self.first_loop:
            return 0
        return self.delay_seconds

    def _call_next(self) -> None:
        super()._call_next()
        self.first_loop = False


retT = Callable[[TaskCallbackT], MetaStruct[TaskCallbackT, Loop]]


@overload
def loop(*, hours: int = ..., minutes: int = ..., seconds: int = ...) -> retT:
    ...


@overload
def loop(timedelta: _timedelta, /) -> retT:
    ...


def loop(
    timedelta: _timedelta | None = None, *, hours: int = 0, minutes: int = 0, seconds: int = 0
) -> retT:
    """
    Run a callback when the bot is started and every time the specified
    time interval has passed.
    """
    if timedelta is None:
        time = _timedelta(hours=hours, minutes=minutes, seconds=seconds)
    else:
        time = timedelta

    def inner(callback: TaskCallbackT) -> MetaStruct[TaskCallbackT, Loop]:
        meta = MetaStruct(callback, Loop(callback, time.total_seconds()))
        Loop._link(meta)
        return meta

    return inner
