from __future__ import annotations

from typing import TYPE_CHECKING

import hikari
from attr import define
from hikari import Member, PartialInteraction, Snowflake, User

if TYPE_CHECKING:
    from typing import Any, Sequence, Type, TypeVar

    from crescent.bot import Mixin

    ContextT = TypeVar("ContextT", bound="BaseContext")


__all__: Sequence[str] = ("BaseContext",)


@define(slots=True)
class BaseContext:
    """Represents the context for interactions"""

    interaction: PartialInteraction
    """The interaction object."""
    app: Mixin
    """The application instance."""
    application_id: Snowflake
    """The ID for the client that this interaction belongs to."""
    type: int
    """The type of the interaction."""
    token: str
    """The token for the interaction."""
    id: Snowflake
    """The ID of the interaction."""
    version: int
    """Version of the interaction system this interaction is under."""

    channel_id: Snowflake
    """The channel ID of the channel that the interaction was used in."""
    guild_id: Snowflake | None
    """The guild ID of the guild that this interaction was used in."""
    user: User
    """The user who triggered this command interaction."""
    member: Member | None
    """The member object for the user that triggered this interaction, if used in a guild."""

    command: str
    """The name of the command."""
    command_type: hikari.CommandType
    group: str | None
    sub_group: str | None
    options: dict[str, Any]
    """The options that were provided by the user."""

    _has_created_message: bool
    """
    Whether the user has responded to this interaction.

    To maintain compatibility with `crescent.Context`, set to `True` when
    creating or editing an interaction response.
    """

    _has_deferred_response: bool
    """
    Whether the user has deferred this interaction.

    To maintain compatibility with `crescent.Context`, set to `True` when
    deferring an interaction response.
    """

    def into(self, context_t: Type[ContextT]) -> ContextT:
        """Convert to a context of a different type."""
        if type(self) is context_t:
            # pyright can't tell this is of type `context_t`
            return self  # pyright: ignore

        return context_t(
            interaction=self.interaction,
            app=self.app,
            application_id=self.application_id,
            type=self.type,
            token=self.token,
            id=self.id,
            version=self.version,
            channel_id=self.channel_id,
            guild_id=self.guild_id,
            user=self.user,
            member=self.member,
            command=self.command,
            command_type=self.command_type,
            group=self.group,
            sub_group=self.sub_group,
            options=self.options,
            # Pyright expects these arguments to start with an underscore but attrs removes that.
            has_created_message=self._has_created_message,  # pyright: ignore
            has_deferred_response=self._has_deferred_response,  # pyright: ignore
        )
