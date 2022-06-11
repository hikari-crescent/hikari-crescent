from typing import Callable, Sequence

from crescent.ext.tasks.task import _Task, TaskCallbackT, _link_task
from crescent.internal import MetaStruct

__all__: Sequence[str] = ("loop",)


class _Loop(_Task):
    def __init__(
        self, callback: TaskCallbackT, *, hours: int, minutes: int, seconds: int
    ) -> None:
        self.timedelta = hours * 360 + minutes * 60 + seconds

        super().__init__(callback)

    def get_time_to_next(self) -> float:
        return self.timedelta


def loop(
    *, hours: int = 0, minutes: int = 0, seconds: int = 0
) -> Callable[[TaskCallbackT], MetaStruct[TaskCallbackT, _Loop]]:
    def inner(callback: TaskCallbackT) -> MetaStruct[TaskCallbackT, _Loop]:
        meta = MetaStruct(callback, _Loop(callback, hours=hours, minutes=minutes, seconds=seconds))
        _link_task(meta)
        return meta

    return inner
