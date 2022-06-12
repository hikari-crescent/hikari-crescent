from typing import Callable, Sequence

from crescent.ext.tasks.task import TaskCallbackT, _link_task, _Task
from crescent.internal import MetaStruct

__all__: Sequence[str] = ("loop",)


class _Loop(_Task):
    def __init__(self, callback: TaskCallbackT, *, hours: int, minutes: int, seconds: int) -> None:
        self.timedelta = hours * 3600 + minutes * 60 + seconds
        self.first_loop = True

        super().__init__(callback)

    def time_to_next(self) -> float:
        if self.first_loop:
            self.first_loop = False
            return 0

        return self.timedelta


def loop(
    *, hours: int = 0, minutes: int = 0, seconds: int = 0
) -> Callable[[TaskCallbackT], MetaStruct[TaskCallbackT, _Loop]]:
    """
    Run a callback when the bot is started and every time the specified
    time interval has passed.
    """

    def inner(callback: TaskCallbackT) -> MetaStruct[TaskCallbackT, _Loop]:
        meta = MetaStruct(callback, _Loop(callback, hours=hours, minutes=minutes, seconds=seconds))
        _link_task(meta)
        return meta

    return inner
