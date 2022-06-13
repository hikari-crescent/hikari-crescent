from datetime import timedelta
from typing import Callable, Sequence

from crescent.ext.tasks.task import TaskCallbackT, link_task, Task
from crescent.internal import MetaStruct

__all__: Sequence[str] = ("loop", "Loop")


class Loop(Task):
    def __init__(self, callback: TaskCallbackT, *, hours: int, minutes: int, seconds: int) -> None:
        self.timedelta = timedelta(hours=hours, minutes=minutes, seconds=seconds).total_seconds()
        self.first_loop = True

        super().__init__(callback)

    def time_to_next(self) -> float:
        if self.first_loop:
            self.first_loop = False
            return 0

        return self.timedelta


def loop(
    *, hours: int = 0, minutes: int = 0, seconds: int = 0
) -> Callable[[TaskCallbackT], MetaStruct[TaskCallbackT, Loop]]:
    """
    Run a callback when the bot is started and every time the specified
    time interval has passed.
    """

    def inner(callback: TaskCallbackT) -> MetaStruct[TaskCallbackT, Loop]:
        meta = MetaStruct(callback, Loop(callback, hours=hours, minutes=minutes, seconds=seconds))
        link_task(meta)
        return meta

    return inner
