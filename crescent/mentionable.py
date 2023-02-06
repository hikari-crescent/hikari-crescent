from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence

    from hikari import CommandInteraction, Role, User

__all__: Sequence[str] = ("Mentionable",)


@dataclass
class Mentionable:
    __slots__ = ("user", "role")

    user: User | None
    role: Role | None

    @classmethod
    def _from_interaction(cls: type[Mentionable], interaction: CommandInteraction) -> Mentionable:
        if not interaction.resolved:
            raise ValueError("Interaction.resolved should not be None")

        if interaction.resolved.users:
            return cls(user=next(iter(interaction.resolved.users.values())), role=None)

        return cls(user=None, role=next(iter(interaction.resolved.roles.values())))

    @property
    def is_user(self) -> bool:
        return self.user is not None

    @property
    def is_role(self) -> bool:
        return self.role is not None

    @property
    def unwrap_user(self) -> User:
        if not self.user:
            raise AttributeError("Mentionable does not have user value")
        return self.user

    @property
    def unwrap_role(self) -> Role:
        if not self.role:
            raise AttributeError("Mentionable does not have role value")
        return self.role
