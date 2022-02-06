from __future__ import annotations

from typing import TYPE_CHECKING, overload

import hikari
from attr import define
from hikari import (
    UNDEFINED,
    CacheAware,
    Guild,
    GuildChannel,
    Member,
    MessageFlag,
    ResponseType,
    RESTAware,
    Snowflake,
    User,
)

from crescent.utils import map_or

if TYPE_CHECKING:
    from typing import Any, Dict, Literal, Optional, Sequence

    from hikari import (
        Embed,
        Message,
        PartialRole,
        PartialUser,
        Resourceish,
        SnowflakeishSequence,
        UndefinedNoneOr,
        UndefinedOr,
        UndefinedType,
    )
    from hikari.api import ComponentBuilder


class RestAndCacheAware(RESTAware, CacheAware):
    ...


__all__: Sequence[str] = ("Context",)


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

    command: str
    command_type: hikari.CommandType
    group: Optional[str]
    sub_group: Optional[str]
    options: Dict[str, Any]

    _has_replied: bool = False
    _used_first_resp: bool = False

    @property
    def channel(self) -> Optional[GuildChannel]:
        return map_or(self.guild_id, self.app.cache.get_guild_channel)

    @property
    def guild(self) -> Optional[Guild]:
        return map_or(self.guild_id, self.app.cache.get_available_guild)

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
            response_type=ResponseType.DEFERRED_MESSAGE_UPDATE,
        )

    @overload
    async def respond(
        self,
        content: UndefinedOr[Any] = UNDEFINED,
        *,
        ensure_message: Literal[True],
        ephemeral: bool = False,
        flags: int | MessageFlag | UndefinedType = UNDEFINED,
        tts: UndefinedOr[bool] = UNDEFINED,
        component: UndefinedOr[ComponentBuilder] = UNDEFINED,
        components: UndefinedOr[Sequence[ComponentBuilder]] = UNDEFINED,
        embed: UndefinedOr[Embed] = UNDEFINED,
        embeds: UndefinedOr[Sequence[Embed]] = UNDEFINED,
        mentions_everyone: UndefinedOr[bool] = UNDEFINED,
        user_mentions: UndefinedOr[SnowflakeishSequence[PartialUser] | bool] = UNDEFINED,
        role_mentions: UndefinedOr[SnowflakeishSequence[PartialRole] | bool] = UNDEFINED,
    ) -> Message:
        ...

    @overload
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
        user_mentions: UndefinedOr[SnowflakeishSequence[PartialUser] | bool] = UNDEFINED,
        role_mentions: UndefinedOr[SnowflakeishSequence[PartialRole] | bool] = UNDEFINED,
        ensure_message: Literal[False] = ...,
    ) -> Optional[Message]:
        ...

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
        user_mentions: UndefinedOr[SnowflakeishSequence[PartialUser] | bool] = UNDEFINED,
        role_mentions: UndefinedOr[SnowflakeishSequence[PartialRole] | bool] = UNDEFINED,
        ensure_message: bool = False,
    ) -> Optional[Message]:

        if ephemeral:
            if flags is UNDEFINED:
                flags = MessageFlag.EPHEMERAL
            else:
                flags |= MessageFlag.EPHEMERAL

        kwargs: dict[str, Any] = dict(
            content=content,
            component=component,
            components=components,
            embed=embed,
            embeds=embeds,
            mentions_everyone=mentions_everyone,
            user_mentions=user_mentions,
            role_mentions=role_mentions,
        )

        if not self._has_replied:
            self._has_replied = True
            self._used_first_resp = True
            await self.app.rest.create_interaction_response(
                **kwargs,
                interaction=self.id,
                token=self.token,
                response_type=ResponseType.MESSAGE_CREATE,
                flags=flags,
                tts=tts,
            )

            if not ensure_message:
                return None

            return await self.app.rest.fetch_interaction_response(self.application_id, self.token)

        if not self._used_first_resp:
            self._used_first_resp = True
            return await self.edit(**kwargs)

        return await self.followup(**kwargs)

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
    ) -> Message:
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
    ) -> Message:
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
            application=self.application_id, token=self.token
        )
