from __future__ import annotations

from typing import TYPE_CHECKING, cast
from attr import define

from hikari import (
    CacheAware,
    Guild,
    GuildChannel,
    Member,
    MessageFlag,
    RESTAware,
    ResponseType,
    UNDEFINED,
    Snowflake,
    User,
)
from crescent.utils import map_or

if TYPE_CHECKING:
    from typing import Any, Type, Sequence, Optional
    from hikari import (
        Embed,
        UndefinedOr,
        UndefinedType,
        PartialRole,
        PartialUser,
        SnowflakeishSequence,
        UndefinedNoneOr,
        Resourceish,
        CommandInteraction
    )
    from hikari.api import ComponentBuilder


class RestAndCacheAware(RESTAware, CacheAware):
    ...


__all__: Sequence[str] = (
    "Context",
)


@define
class Context:
    """Represents the context for interactions"""

    app: RestAndCacheAware
    application_id: Snowflake
    type: int
    token: str
    id: Snowflake
    version: int

    channel_id: Snowflake
    guild_id: Optional[Snowflake]
    user: User
    member: Optional[Member]

    _has_replied: bool = False
    _used_first_resp: bool = False

    @classmethod
    def _from_command_interaction(cls: Type[Context], interaction: CommandInteraction) -> Context:
        return cls(
            app=cast(RestAndCacheAware, interaction.app),
            application_id=interaction.application_id,
            type=interaction.type,
            token=interaction.token,
            id=interaction.id,
            version=interaction.version,
            channel_id=interaction.channel_id,
            guild_id=interaction.guild_id,
            user=interaction.user,
            member=interaction.member,
        )

    @property
    def channel(self) -> Optional[GuildChannel]:
        return map_or(
            self.guild_id,
            self.app.cache.get_guild_channel
        )

    @property
    def guild(self) -> Optional[Guild]:
        return map_or(
            self.guild_id,
            self.app.cache.get_available_guild
        )

    async def defer(self, ephemeral: bool = False):
        self._has_replied = True
        await self.app.rest.create_interaction_response(
            interaction=self.id,
            token=self.token,
            flags=MessageFlag.EPHEMERAL if ephemeral else UNDEFINED,
            response_type=ResponseType.DEFERRED_MESSAGE_CREATE,
        )

    async def defer_update(self, ephemeral: bool = False):
        self._has_replied = True
        await self.app.rest.create_interaction_response(
            interaction=self.id,
            token=self.token,
            flags=MessageFlag.EPHEMERAL if ephemeral else UNDEFINED,
            response_type=ResponseType.DEFERRED_MESSAGE_UPDATE
        )

    async def respond(
        self,
        content: UndefinedOr[Any] = UNDEFINED,
        *,
        ephemeral: bool = False,
        flags: int | MessageFlag | UndefinedType = UNDEFINED,
        tts: UndefinedOr[bool] = UNDEFINED,
        component: UndefinedOr[ComponentBuilder] = UNDEFINED,
        components: UndefinedOr[Sequence[ComponentBuilder]] = UNDEFINED,
        embed: UndefinedOr[Embed] = UNDEFINED,
        embeds: UndefinedOr[Sequence[Embed]] = UNDEFINED,
        mentions_everyone: UndefinedOr[bool] = UNDEFINED,
        user_mentions: UndefinedOr[
            SnowflakeishSequence[PartialUser] | bool
        ] = UNDEFINED,
        role_mentions: UndefinedOr[
            SnowflakeishSequence[PartialRole] | bool
        ] = UNDEFINED,
    ) -> None:

        if ephemeral:
            if flags is UNDEFINED:
                flags = MessageFlag.EPHEMERAL
            else:
                flags |= MessageFlag.EPHEMERAL

        if not self._has_replied:
            self._has_replied = True
            self._used_first_resp = True
            return await self.app.rest.create_interaction_response(
                interaction=self.id,
                token=self.token,
                content=content,
                response_type=ResponseType.MESSAGE_CREATE,
                flags=flags,
                tts=tts,
                component=component,
                components=components,
                embed=embed,
                embeds=embeds,
                mentions_everyone=mentions_everyone,
                user_mentions=user_mentions,
                role_mentions=role_mentions
            )

        if not self._used_first_resp:
            self._used_first_resp = True
            return await self.edit(
                content=content,
                component=component,
                components=components,
                embed=embed,
                embeds=embeds,
                mentions_everyone=mentions_everyone,
                user_mentions=user_mentions,
                role_mentions=role_mentions
            )

        return await self.followup(
            content=content,
            component=component,
            components=components,
            embed=embed,
            embeds=embeds,
            mentions_everyone=mentions_everyone,
            user_mentions=user_mentions,
            role_mentions=role_mentions,
        )

    async def edit(
        self,
        content: UndefinedNoneOr[Any] = UNDEFINED,
        *,
        attachment: UndefinedOr[Resourceish] = UNDEFINED,
        attachments: UndefinedOr[Sequence[Resourceish]] = UNDEFINED,
        component: UndefinedNoneOr[ComponentBuilder] = UNDEFINED,
        components: UndefinedNoneOr[Sequence[ComponentBuilder]] = UNDEFINED,
        embed: UndefinedNoneOr[Embed] = UNDEFINED,
        embeds: UndefinedNoneOr[Sequence[Embed]] = UNDEFINED,
        replace_attachments: bool = False,
        mentions_everyone: UndefinedOr[bool] = UNDEFINED,
        user_mentions: UndefinedOr[SnowflakeishSequence[PartialUser] | bool] = UNDEFINED,
        role_mentions: UndefinedOr[SnowflakeishSequence[PartialRole] | bool] = UNDEFINED,

    ):
        return await self.app.rest.edit_interaction_response(
            application=self.application_id,
            token=self.token,
            content=content,
            attachment=attachment,
            attachments=attachments,
            component=component,
            components=components,
            embed=embed,
            embeds=embeds,
            replace_attachments=replace_attachments,
            mentions_everyone=mentions_everyone,
            user_mentions=user_mentions,
            role_mentions=role_mentions,
        )

    async def followup(
        self,
        content: UndefinedNoneOr[Any] = UNDEFINED,
        *,
        attachment: UndefinedOr[Resourceish] = UNDEFINED,
        attachments: UndefinedOr[Sequence[Resourceish]] = UNDEFINED,
        component: UndefinedOr[ComponentBuilder] = UNDEFINED,
        components: UndefinedOr[Sequence[ComponentBuilder]] = UNDEFINED,
        embed: UndefinedOr[Embed] = UNDEFINED,
        embeds: UndefinedOr[Sequence[Embed]] = UNDEFINED,
        mentions_everyone: UndefinedOr[bool] = UNDEFINED,
        user_mentions: UndefinedOr[SnowflakeishSequence[PartialUser] | bool] = UNDEFINED,
        role_mentions: UndefinedOr[SnowflakeishSequence[PartialRole] | bool] = UNDEFINED,
    ):
        return await self.app.rest.execute_webhook(
            webhook=self.application_id,
            token=self.token,
            content=content,
            attachment=attachment,
            attachments=attachments,
            component=component,
            components=components,
            embed=embed,
            embeds=embeds,
            mentions_everyone=mentions_everyone,
            user_mentions=user_mentions,
            role_mentions=role_mentions,
        )

    async def delete(self):
        await self.app.rest.delete_interaction_response(
            application=self.application_id,
            token=self.token,
        )
