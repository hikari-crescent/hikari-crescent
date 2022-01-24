from typing import Any, Awaitable, Callable, Sequence

__all__: Sequence[str] = ("CommandCallback",)

CommandCallback = Callable[..., Awaitable[Any]]
