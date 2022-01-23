from __future__ import annotations

from typing import TYPE_CHECKING
from attr import define

from hikari import MessageResponseMixin, PartialInteraction

if TYPE_CHECKING:
    from typing import Type, Sequence

__all__: Sequence[str] = (
    "Context",
)


@define
class Context(MessageResponseMixin):
    """Represents the context for interactions"""

    @classmethod
    def _from_partial_interaction(cls: Type[Context], interaction: PartialInteraction) -> Context:
        return cls(
            app=interaction.app,
            application_id=interaction.application_id,
            type=interaction.type,
            token=interaction.token,
            id=interaction.id,
            version=interaction.version,
        )
