from __future__ import annotations

from asyncio import Task
from asyncio import create_task as _create_task
from typing import Any, Awaitable, Coroutine, Sequence, Set, TypeVar

__all__: Sequence[str] = ("create_task",)

T = TypeVar("T")

_background_tasks: Set[Any] = set()


def create_task(_task: Coroutine[Any, Any, T] | Awaitable[T]) -> Task[T]:
    task: Task[Any] = _create_task(_task)  # type: ignore

    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.remove)

    return task
