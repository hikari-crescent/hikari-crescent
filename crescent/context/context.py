from __future__ import annotations

from typing import TYPE_CHECKING, overload

from hikari import (
    UNDEFINED,
    GatewayGuild,
    GuildThreadChannel,
    MessageFlag,
    PermissibleGuildChannel,
    ResponseType,
)
from hikari.traits import CacheAware

from crescent.context.base_context import BaseContext

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

    interaction: CommandInteraction  # pyright: ignore [reportIncompatibleVariableOverride]

    @property
    def channel(self) -> PermissibleGuildChannel | GuildThreadChannel | None:
        """Get this context's guild channel or thread from the cache.

        > 📝 This will always be `None` for interactions triggered in a DM channel.
        """
        if isinstance(self.app, CacheAware):
            return self.app.cache.get_guild_channel(self.channel_id) or self.app.cache.get_thread(
                self.channel_id
            )
        return None

    @property
    def guild(self) -> GatewayGuild | None:
        """Get this context's guild from the cache."""
        return self.interaction.get_guild()

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
        """
        Respond to an interaction. This function can be used multiple times
        for one interaction,

        ### Example
        ```python
        @client.include
        @crescent.command
        async def command(ctx: crescent.Context):
            # Initial response
            await ctx.respond("hello")
            # After the first response, a followup response will be sent.
            await ctx.respond("word")
        ```

        > 📝 Message flags are ignored in followup responses.

        Args:
            content:
                The content to send.
            ephermial:
                Send this message as ephermial if set to true. Ephermial
                messages can be dismissed by the user, similar to Clyde
                messages. This kwarg only affects the initial response to an
                interaction.
            flags:
                Message flags to send with the message. You do not need to use
                this, and exists for compatibility in the future. Instead set
                the `ephermial` kwarg  to `True`.
            tts:
                If true, send a text to speech message.
            attachment:
                A single attachment to send.
            attachments:
                A list of attachments to send.
            component:
                A single component to send.
            components:
                A list of components to send.
            embed:
                A single embed to send.
            embeds:
                A list of embeds to send.
            mentions_everyone:
                Allow `@everyone` and `@here` to ping users if set to `True`.
            user_mentions:
                If `True`, all mentioned users will be sent a notification. If
                a list of users is provided, only those users will be mentioned.
            role_mentions:
                If `True`, all mentioned roles will be sent a notification. If
                a list of roles is provided, only those roles will be mentioned.
            ensure_message:
                A message is not returned the first time you use
                `Context.respond`. Set `ensure_message=True` to automatically
                fetch a message and return it.
        """
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
        """
        Edit the previous response to this interaction.

        ### Example
        ```python
        import asyncio

        @client.include
        @crescent.command
        async def command(ctx: crescent.Context):
            await ctx.respond("hello there")
            await asyncio.sleep(3)
            await ctx.edit("general kenobi")
        ```

        > 📝 Message flags are ignored in followup responses.

        Args:
            content:
                The content to send.
            attachment:
                A single attachment to send.
            attachments:
                A list of attachments to send.
            component:
                A single component to send.
            components:
                A list of components to send.
            embed:
                A single embed to send.
            embeds:
                A list of embeds to send.
            mentions_everyone:
                Allow `@everyone` and `@here` to ping users if set to `True`.
            user_mentions:
                If `True`, all mentioned users will be sent a notification. If
                a list of users is provided, only those users will be mentioned.
            role_mentions:
                If `True`, all mentioned roles will be sent a notification. If
                a list of roles is provided, only those roles will be mentioned.
        """
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
        """
        Delete the previous response to this interaction.

        ### Example
        ```python
        import asyncio

        @client.include
        @crescent.command
        async def command(ctx: crescent.Context):
            await ctx.respond("im going to disappear")
            await asyncio.sleep(3)
            await ctx.delete()
        ```
        """
        await self.app.rest.delete_interaction_response(
            application=self.application_id, token=self.token
        )
