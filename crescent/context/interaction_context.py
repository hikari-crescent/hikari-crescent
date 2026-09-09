from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from asyncio import Future
    from collections.abc import Sequence

    import hikari
    from hikari import Locale, Member, PartialInteraction, Snowflake, User
    from hikari.api import InteractionResponseBuilder

    from crescent.client import Client, GatewayTraits, RESTTraits


__all__ = ("InteractionContext",)


@dataclass(slots=True)
class InteractionContext:
    """Represents the context for interactions"""

    interaction: PartialInteraction
    """The interaction object."""
    app: GatewayTraits | RESTTraits
    """The application instance."""
    client: Client
    """The crescent Client instance."""
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
    registered_guild_id: Snowflake | None
    """The guild ID of the guild that this command is registered to."""
    user: User
    """The user who triggered this command interaction."""
    member: Member | None
    """The member object for the user that triggered this interaction, if used in a guild."""
    entitlements: Sequence[hikari.Entitlement]
    """For monetized apps, any entitlements involving this user. Represents access to SKUs."""
    locale: Locale

    command: str
    """The name of the command."""
    command_type: hikari.CommandType
    group: str | None
    sub_group: str | None
    options: dict[str, Any]
    """The options that were provided by the user."""

    _has_created_response: bool
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

    _rest_interaction_future: Future[InteractionResponseBuilder] | None
    """Future used to handle the callback for RESTBot."""

    @property
    def _unset_future(self) -> Future[InteractionResponseBuilder] | None:
        """Returns the future for the response, if it exists and hasn't already been set.

        Will only exist for RESTBot."""

        if self._rest_interaction_future and not self._rest_interaction_future.done():
            return self._rest_interaction_future
        return None
