from __future__ import annotations

from asyncio import Task
from asyncio import create_task as _create_task
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Coroutine

__all__ = ("create_task",)

_background_tasks: set[Task[object]] = set()


def create_task[T](_task: Coroutine[Any, Any, T]) -> Task[T]:
    task = _create_task(_task)

    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.remove)

    return task
