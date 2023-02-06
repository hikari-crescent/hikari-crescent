from __future__ import annotations

from typing import TYPE_CHECKING, overload

from hikari import UNDEFINED, Guild, GuildChannel, MessageFlag, ResponseType
from hikari.traits import CacheAware

from crescent.context.base_context import BaseContext
from crescent.utils import map_or

if TYPE_CHECKING:
    from typing import Any, Literal, Sequence

    from hikari import (
        Attachment,
        CommandInteraction,
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


__all__: Sequence[str] = ("Context",)


class Context(BaseContext):
    """Represents the context for command interactions"""

    interaction: CommandInteraction

    @property
    def channel(self) -> GuildChannel | None:
        if isinstance(self.app, CacheAware):
            return self.app.cache.get_guild_channel(self.channel_id)
        return None

    @property
    def guild(self) -> Guild | None:
        if isinstance(self.app, CacheAware):
            return map_or(self.guild_id, self.app.cache.get_available_guild)
        return None

    async def defer(self, ephemeral: bool = False) -> None:
        """
        Defer this interaction response, allowing you to respond within the next 15
        minutes.
        """

        if future := self._unset_future:
            future.set_result(self.interaction.build_deferred_response())
        else:
            await self.app.rest.create_interaction_response(
                interaction=self.id,
                token=self.token,
                flags=MessageFlag.EPHEMERAL if ephemeral else UNDEFINED,
                response_type=ResponseType.DEFERRED_MESSAGE_CREATE,
            )
        self._has_deferred_response = True

    @overload
    async def respond(
        self,
        content: UndefinedOr[Any] = UNDEFINED,
        *,
        ensure_message: Literal[True],
        ephemeral: bool = False,
        flags: int | MessageFlag | UndefinedType = UNDEFINED,
        tts: UndefinedOr[bool] = UNDEFINED,
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
        ...

    @overload
    async def respond(
        self,
        content: UndefinedOr[Any] = UNDEFINED,
        *,
        ephemeral: bool = False,
        flags: int | MessageFlag | UndefinedType = UNDEFINED,
        tts: UndefinedOr[bool] = UNDEFINED,
        attachment: UndefinedOr[Resourceish] = UNDEFINED,
        attachments: UndefinedOr[Sequence[Resourceish]] = UNDEFINED,
        component: UndefinedOr[ComponentBuilder] = UNDEFINED,
        components: UndefinedOr[Sequence[ComponentBuilder]] = UNDEFINED,
        embed: UndefinedOr[Embed] = UNDEFINED,
        embeds: UndefinedOr[Sequence[Embed]] = UNDEFINED,
        mentions_everyone: UndefinedOr[bool] = UNDEFINED,
        user_mentions: UndefinedOr[SnowflakeishSequence[PartialUser] | bool] = UNDEFINED,
        role_mentions: UndefinedOr[SnowflakeishSequence[PartialRole] | bool] = UNDEFINED,
        ensure_message: Literal[False] = ...,
    ) -> Message | None:
        ...

    async def respond(
        self,
        content: UndefinedOr[Any] = UNDEFINED,
        *,
        ephemeral: bool = False,
        flags: int | MessageFlag | UndefinedType = UNDEFINED,
        tts: UndefinedOr[bool] = UNDEFINED,
        attachment: UndefinedOr[Resourceish] = UNDEFINED,
        attachments: UndefinedOr[Sequence[Resourceish]] = UNDEFINED,
        component: UndefinedOr[ComponentBuilder] = UNDEFINED,
        components: UndefinedOr[Sequence[ComponentBuilder]] = UNDEFINED,
        embed: UndefinedOr[Embed] = UNDEFINED,
        embeds: UndefinedOr[Sequence[Embed]] = UNDEFINED,
        mentions_everyone: UndefinedOr[bool] = UNDEFINED,
        user_mentions: UndefinedOr[SnowflakeishSequence[PartialUser] | bool] = UNDEFINED,
        role_mentions: UndefinedOr[SnowflakeishSequence[PartialRole] | bool] = UNDEFINED,
        ensure_message: bool = False,
    ) -> Message | None:
        if ephemeral:
            if flags is UNDEFINED:
                flags = MessageFlag.EPHEMERAL
            else:
                flags |= MessageFlag.EPHEMERAL

        kwargs: dict[str, Any] = dict(
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

        if not (self._has_deferred_response or self._has_created_message):
            if future := self._unset_future:
                resp = (
                    self.interaction.build_response()
                    .set_content(content)
                    .set_user_mentions(user_mentions)
                    .set_role_mentions(role_mentions)
                    .set_mentions_everyone(mentions_everyone)
                    .set_flags(flags)
                    .set_tts(tts)
                )
                if attachments:
                    for a in attachments:
                        resp = resp.add_attachment(a)
                if attachment:
                    resp = resp.add_attachment(attachment)
                if components:
                    for c in components:
                        resp = resp.add_component(c)
                if component:
                    resp = resp.add_component(component)
                if embeds:
                    for e in embeds:
                        resp = resp.add_embed(e)
                if embed:
                    resp = resp.add_embed(embed)

                future.set_result(resp)
            else:
                await self.app.rest.create_interaction_response(
                    **kwargs,
                    tts=tts,
                    flags=flags,
                    interaction=self.id,
                    token=self.token,
                    response_type=ResponseType.MESSAGE_CREATE,
                )

            self._has_created_message = True

            if not ensure_message:
                return None

            return await self.app.rest.fetch_interaction_response(self.application_id, self.token)

        if self._has_deferred_response and not self._has_created_message:
            res = await self.edit(**kwargs)
            self._has_created_message = True
            return res

        return await self.followup(**kwargs)

    async def edit(
        self,
        content: UndefinedNoneOr[Any] = UNDEFINED,
        *,
        attachment: UndefinedNoneOr[Resourceish | Attachment] = UNDEFINED,
        attachments: UndefinedNoneOr[Sequence[Resourceish | Attachment]] = UNDEFINED,
        component: UndefinedNoneOr[ComponentBuilder] = UNDEFINED,
        components: UndefinedNoneOr[Sequence[ComponentBuilder]] = UNDEFINED,
        embed: UndefinedNoneOr[Embed] = UNDEFINED,
        embeds: UndefinedNoneOr[Sequence[Embed]] = UNDEFINED,
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

    async def delete(self) -> None:
        await self.app.rest.delete_interaction_response(
            application=self.application_id, token=self.token
        )
