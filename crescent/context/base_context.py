from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import hikari
from hikari import Locale, Member, PartialInteraction, Snowflake, User

if TYPE_CHECKING:
    from asyncio import Future
    from typing import Any, Sequence, Type, TypeVar

    from hikari.api import InteractionResponseBuilder

    from crescent.client import Client, GatewayTraits, RESTTraits

    ContextT = TypeVar("ContextT", bound="BaseContext")


__all__: Sequence[str] = ("BaseContext",)


@dataclass
class BaseContext:
    """Represents the context for interactions"""

    __slots__ = (
        "interaction",
        "app",
        "client",
        "application_id",
        "type",
        "token",
        "id",
        "version",
        "channel_id",
        "guild_id",
        "user",
        "member",
        "locale",
        "command",
        "command_type",
        "group",
        "sub_group",
        "options",
        "_has_created_message",
        "_has_deferred_response",
        "_rest_interaction_future",
    )

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
    user: User
    """The user who triggered this command interaction."""
    member: Member | None
    """The member object for the user that triggered this interaction, if used in a guild."""
    locale: Locale

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

    _rest_interaction_future: Future[InteractionResponseBuilder] | None

    @property
    def _unset_future(self) -> Future[InteractionResponseBuilder] | None:
        """Returns the future for the response, if it exists and hasn't already been set.

        Will only exist for RESTBot."""

        if self._rest_interaction_future and not self._rest_interaction_future.done():
            return self._rest_interaction_future
        return None

    def into(self, context_t: Type[ContextT]) -> ContextT:
        """Convert to a context of a different type."""
        if type(self) is context_t:
            # pyright can't tell this is of type `context_t`
            return self  # pyright: ignore

        return context_t(
            interaction=self.interaction,
            app=self.app,
            client=self.client,
            application_id=self.application_id,
            type=self.type,
            token=self.token,
            id=self.id,
            version=self.version,
            channel_id=self.channel_id,
            guild_id=self.guild_id,
            user=self.user,
            member=self.member,
            locale=self.locale,
            command=self.command,
            command_type=self.command_type,
            group=self.group,
            sub_group=self.sub_group,
            options=self.options,
            _has_created_message=self._has_created_message,
            _has_deferred_response=self._has_deferred_response,
            _rest_interaction_future=self._rest_interaction_future,
        )
