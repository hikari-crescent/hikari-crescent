from datetime import datetime
from typing import Callable, Sequence

from croniter import croniter

from crescent.ext.tasks.task import TaskCallbackT, _link_task, _Task
from crescent.internal import MetaStruct

__all__: Sequence[str] = ("cronjob",)


class _Cronjob(_Task):
    def __init__(self, cron: str, callback: TaskCallbackT) -> None:
        self.cron = croniter(cron, datetime.now())

        super().__init__(callback)

    def time_to_next(self) -> float:
        call_next_at: datetime = self.cron.get_next(datetime)
        time_to_next = call_next_at - datetime.now()
        return time_to_next.total_seconds()


def cronjob(cron: str, /) -> Callable[[TaskCallbackT], MetaStruct[TaskCallbackT, _Cronjob]]:
    """
    Run a task at the time specified by the cron schedule expression.
    """

    def inner(callback: TaskCallbackT) -> MetaStruct[TaskCallbackT, _Cronjob]:
        meta = MetaStruct(callback, _Cronjob(cron, callback))
        _link_task(meta)
        return meta

    return inner
