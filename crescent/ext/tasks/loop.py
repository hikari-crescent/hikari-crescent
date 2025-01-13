from __future__ import annotations

from datetime import timedelta as _timedelta
from typing import Callable, Sequence, overload

from crescent.ext.tasks.task import Task, TaskCallbackT
from crescent.internal import Includable

__all__: Sequence[str] = ("loop", "Loop")


class Loop(Task):
    def __init__(self, callback: TaskCallbackT, delay_seconds: float) -> None:
        self.delay_seconds: float = delay_seconds
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

    @overload
    def set_interval(
        self, *, hours: int = ..., minutes: int = ..., seconds: int = ...
    ) -> None: ...

    @overload
    def set_interval(self, timedelta: _timedelta, /) -> None: ...

    def set_interval(
        self,
        timedelta: _timedelta | None = None,
        *,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
    ) -> None:
        """
        Cancel the currently scheduled task and schedule the next task and future tasks
        with a new wait time.

        ## Example
        ```
        from datetime import datetime
        import crescent
        from crescent.ext import tasks

        bot = hikari.GatewayBot("...")
        client = crescent.Client(bot)

        @client.include
        @tasks.loop(seconds=1)
        async def my_task():
            print(datetime.now())

        @client.include
        @crescent.command
        async def set_interval(ctx: crescent.Context, interval: int):
            print(f"setting new interval to {interval}")
            my_task.metadata.set_interval(seconds=interval)
            await ctx.respond(f"Set new interval to {interval}s")
        ```
        """
        timedelta = timedelta or _timedelta(hours=hours, minutes=minutes, seconds=seconds)
        self.delay_seconds = timedelta.total_seconds()

        # We do not want to schedule a new task if the loop is not currently running
        # because that would unintentionally start the loop again.
        if self.running:
            self.stop()
            self.start()


retT = Callable[[TaskCallbackT], Includable[Loop]]


@overload
def loop(*, hours: int = ..., minutes: int = ..., seconds: int = ...) -> retT: ...


@overload
def loop(timedelta: _timedelta, /) -> retT: ...


def loop(
    timedelta: _timedelta | None = None, *, hours: int = 0, minutes: int = 0, seconds: int = 0
) -> retT:
    """
    Run a callback when the bot is started and every time the specified
    time interval has passed.
    """
    timedelta = timedelta or _timedelta(hours=hours, minutes=minutes, seconds=seconds)

    def inner(callback: TaskCallbackT) -> Includable[Loop]:
        includable = Includable(Loop(callback, timedelta.total_seconds()))
        Loop._link(includable)
        return includable

    return inner
