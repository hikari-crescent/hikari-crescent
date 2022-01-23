from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar
from attr import define

if TYPE_CHECKING:
    from typing import Any, Awaitable, Callable, Sequence, Optional

T = TypeVar("T")


__all__: Sequence[str] = (
    "MetaStruct",
)


@define
class MetaStruct(Generic[T]):
    callback: Callable[..., Awaitable[Any]]
    metadata: T
    manager: Optional[Any]

    is_method: bool = False
