from datetime import datetime
from typing import Callable, Sequence

from croniter import croniter

from crescent.ext.tasks.task import Task, TaskCallbackT
from crescent.internal import Includable

__all__: Sequence[str] = ("cronjob", "Cronjob")


class Cronjob(Task):
    def __init__(self, cron: str, callback: TaskCallbackT, *, on_startup: bool) -> None:
        self.cron: croniter = croniter(cron, datetime.now())
        self.on_startup = on_startup

        super().__init__(callback)

    def _next_iteration(self) -> float:
        if self.on_startup:
            return 0

        call_next_at: datetime = self.cron.get_next(datetime)
        time_to_next = call_next_at - datetime.now()
        return time_to_next.total_seconds()

    def _call_next(self) -> None:
        super()._call_next()
        self.on_startup = False


def cronjob(
    cron: str, /, on_startup: bool = False
) -> Callable[[TaskCallbackT], Includable[Cronjob]]:
    """
    Run a task at the time specified by the cron schedule expression.

    Args:
        cron:
            The cronjob used to schedule when the callback is run. `croniter` is used
            for parsing cron expressions.
        on_startup:
            If `True`, run the callback when this task is started.
    """

    def inner(callback: TaskCallbackT) -> Includable[Cronjob]:
        includable = Includable(Cronjob(cron, callback, on_startup=on_startup))
        Cronjob._link(includable)
        return includable

    return inner
