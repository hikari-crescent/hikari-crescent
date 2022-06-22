from datetime import datetime
from typing import Callable, Sequence

from croniter import croniter

from crescent.ext.tasks.task import Task, TaskCallbackT
from crescent.internal import MetaStruct

__all__: Sequence[str] = ("cronjob", "Cronjob")


class Cronjob(Task):
    def __init__(self, cron: str, callback: TaskCallbackT) -> None:
        self.cron: croniter = croniter(cron, datetime.now())

        super().__init__(callback)

    def _next_iteration(self) -> float:
        call_next_at: datetime = self.cron.get_next(datetime)
        time_to_next = call_next_at - datetime.now()
        return time_to_next.total_seconds()


def cronjob(cron: str, /) -> Callable[[TaskCallbackT], MetaStruct[TaskCallbackT, Cronjob]]:
    """
    Run a task at the time specified by the cron schedule expression.
    """

    def inner(callback: TaskCallbackT) -> MetaStruct[TaskCallbackT, Cronjob]:
        meta = MetaStruct(callback, Cronjob(cron, callback))
        Cronjob._link(meta)
        return meta

    return inner
