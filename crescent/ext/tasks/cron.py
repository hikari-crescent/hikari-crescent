from datetime import datetime
from typing import Callable, Sequence

from crescent.ext.tasks.task import Task, TaskCallbackT
from crescent.internal import Includable

__all__: Sequence[str] = ("cronjob", "Cronjob")


class Cronjob(Task):
    def __init__(self, cron: str, callback: TaskCallbackT, *, first_loop: bool) -> None:
        try:
            from croniter import croniter
        except ImportError:
            raise ModuleNotFoundError(
                "`hikari-crescent[cron]` must be installed to use `cooldowns.cronjob`."
            )

        self.cron: croniter = croniter(cron, datetime.now())
        self.first_loop: bool = first_loop

        super().__init__(callback)

    def _next_iteration(self) -> float:
        if self.first_loop:
            return 0

        call_next_at: datetime = self.cron.get_next(datetime)
        time_to_next = call_next_at - datetime.now()
        return time_to_next.total_seconds()

    def _call_next(self) -> None:
        super()._call_next()
        self.first_loop = False


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
        includable = Includable(Cronjob(cron, callback, first_loop=on_startup))
        Cronjob._link(includable)
        return includable

    return inner
