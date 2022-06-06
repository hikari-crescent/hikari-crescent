from asyncio import ensure_future, get_event_loop
from datetime import datetime
from crescent import Bot
from typing import Awaitable, Callable
from croniter import croniter

TaskCallbackT = Callable[[Bot], Awaitable[None]]


class _Task:
    def __init__(self, cron: str, callback: TaskCallbackT) -> None:
        self.cron = croniter(cron, datetime.now())
        self.event_loop = get_event_loop()

    def start(self):
        ensure_future(self.task())

    async def task(self):
        date = self.cron.get_next(datetime)
        print(date)


def cronjob(cron: str, callback: Callable[[], Awaitable[None]]):
    pass
