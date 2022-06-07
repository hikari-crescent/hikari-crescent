from asyncio import ensure_future, get_event_loop
from datetime import datetime
from crescent.internal.meta_struct import MetaStruct
from typing import Awaitable, Callable
from croniter import croniter

TaskCallbackT = Callable[[], Awaitable[None]]


class _Task:
    def __init__(self, cron: str, callback: TaskCallbackT) -> None:
        self.cron = croniter(cron, datetime.now())
        self.event_loop = get_event_loop()
        self.callback = callback
        self.running = True

    def start(self):
        self.call_next()

    def stop(self):
        self.running = False

    def call_async(self):
        if not self.running:
            return
        ensure_future(self.callback())
        self.call_next()

    def call_next(self):
        call_next_at = self.cron.get_next(datetime)
        time_to_next = call_next_at - datetime.now()
        self.event_loop.call_later(time_to_next.total_seconds(), self.call_async)


def _on_app_set(self: MetaStruct[TaskCallbackT, _Task]) -> None:
    self.metadata.start()


def _unload(self: MetaStruct[TaskCallbackT, _Task]) -> None:
    self.metadata.stop()


def cronjob(cron: str) -> MetaStruct[TaskCallbackT, _Task]:
    def inner(callback: TaskCallbackT):
        return MetaStruct(
            callback,
            _Task(cron, callback),
            app_set_hooks=[_on_app_set],
            plugin_unload_hook=_unload,
        )

    return inner