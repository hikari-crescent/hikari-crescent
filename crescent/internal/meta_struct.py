from typing import Any, Awaitable, Callable, Generic, Sequence, TypeVar, Optional

from attr import define

T = TypeVar("T")


__all__: Sequence[str] = (
    "MetaStruct",
)


@define
class MetaStruct(Generic[T]):
    callback: Callable[..., Awaitable[Any]]
    metadata: T
    manager: Optional[Any]
