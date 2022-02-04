from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Mapping, cast

import hikari
from attr import define
from hikari import (
    UNDEFINED,
    CacheAware,
    CommandInteractionOption,
    CommandType,
    Guild,
    GuildChannel,
    Member,
    MessageFlag,
    OptionType,
    ResponseType,
    RESTAware,
    Snowflake,
    User,
)

from crescent.mentionable import Mentionable
from crescent.utils import map_or, unwrap

if TYPE_CHECKING:
    from typing import Any, Optional, Sequence, Type

    from hikari import (
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

    from crescent.typedefs import OptionTypesT


class RestAndCacheAware(RESTAware, CacheAware):
    ...


__all__: Sequence[str] = ("Context",)


_VALUE_TYPE_LINK: Dict[OptionType | int, str] = {
    OptionType.ROLE: "roles",
    OptionType.USER: "users",
    OptionType.CHANNEL: "channels",
}


def _options_to_kwargs(
    interaction: CommandInteraction,
    options: Optional[Sequence[CommandInteractionOption]],
) -> Dict[str, Any]:
    if not options:
        return {}

    return {option.name: _extract_value(option, interaction) for option in options}


def _extract_value(option: CommandInteractionOption, interaction: CommandInteraction) -> Any:
    if option.type is OptionType.MENTIONABLE:
        return Mentionable._from_interaction(interaction)

    resolved_type: Optional[str] = _VALUE_TYPE_LINK.get(option.type)

    if resolved_type is None:
        return option.value

    resolved = getattr(interaction.resolved, resolved_type)
    return resolved[option.value]


def _resolved_data_to_kwargs(interaction: CommandInteraction) -> Dict[str, Message | User]:
    if not interaction.resolved:
        raise ValueError("interaction.resoved should be defined when running this function")

    if interaction.resolved.messages:
        return {"message": next(iter(interaction.resolved.messages.values()))}
    if interaction.resolved.members:
        return {"user": next(iter(interaction.resolved.members.values()))}
    if interaction.resolved.users:
        return {"user": next(iter(interaction.resolved.users.values()))}

    raise AttributeError(
        "interaction.resolved did not have property `messages`, `members`, or `users`"
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

    command: str
    command_type: hikari.CommandType
    group: Optional[str]
    sub_group: Optional[str]
    options: Dict[str, Any]

    _has_replied: bool = False
    _used_first_resp: bool = False

    @classmethod
    def _from_command_interaction(cls: Type[Context], interaction: CommandInteraction) -> Context:
        name: str = interaction.command_name
        group: Optional[str] = None
        sub_group: Optional[str] = None
        options = interaction.options

        if options:
            option = options[0]
            if option.type == 1:
                group = name
                name = option.name
                options = option.options
            elif option.type == 2:
                group = interaction.command_name
                sub_group = option.name
                name = unwrap(option.options)[0].name

        callback_options: Mapping[str, OptionTypesT | Message | User]
        if interaction.command_type is CommandType.SLASH:
            callback_options = _options_to_kwargs(interaction, options)
        else:
            callback_options = _resolved_data_to_kwargs(interaction)

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
            command=name,
            group=group,
            sub_group=sub_group,
            command_type=hikari.CommandType(interaction.command_type),
            options=callback_options,
        )

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
            return await self.app.rest.create_interaction_response(
                **kwargs,
                interaction=self.id,
                token=self.token,
                response_type=ResponseType.MESSAGE_CREATE,
                flags=flags,
                tts=tts,
            )

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
            application=self.application_id,
            token=self.token,
        )
