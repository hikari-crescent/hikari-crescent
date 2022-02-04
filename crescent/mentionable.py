from __future__ import annotations

from typing import TYPE_CHECKING

from attr import define

if TYPE_CHECKING:
    from typing import Optional, Sequence, Type

    from hikari import CommandInteraction, Role, User

__all__: Sequence[str] = ("Mentionable",)


@define
class Mentionable:
    user: Optional[User]
    role: Optional[Role]

    @classmethod
    def _from_interaction(cls: Type[Mentionable], interaction: CommandInteraction) -> Mentionable:
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
