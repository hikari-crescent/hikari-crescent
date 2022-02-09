from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING, Mapping, Optional, cast

from hikari import UNDEFINED, CommandType, OptionType

from crescent.context import Context
from crescent.exceptions import CommandNotFoundError
from crescent.internal.app_command import Unique
from crescent.mentionable import Mentionable
from crescent.utils import unwrap

if TYPE_CHECKING:
    from typing import Any, Dict, Sequence

    from hikari import (
        CommandInteraction,
        CommandInteractionOption,
        InteractionCreateEvent,
        Message,
        Snowflake,
        User,
    )

    from crescent.bot import Bot
    from crescent.context import RestAndCacheAware
    from crescent.internal import AppCommandMeta, MetaStruct
    from crescent.typedefs import CommandCallbackT, OptionTypesT


__all__: Sequence = ("handle_resp",)


async def handle_resp(event: InteractionCreateEvent):

    interaction = event.interaction
    bot = event.app

    if TYPE_CHECKING:
        interaction = cast(CommandInteraction, interaction)
        bot = cast(Bot, bot)

    ctx = _context_from_interaction_resp(interaction)
    command = _get_command(
        bot, ctx.command, int(ctx.command_type), ctx.guild_id, ctx.group, ctx.sub_group
    )

    for hook in command.metadata.hooks:
        hook_res = await hook(ctx)

        if hook_res and hook_res.exit:
            break

    else:
        try:
            await command.callback(ctx, **ctx.options)
        except Exception as e:
            if func := command.app._error_handler.registry.get(e.__class__):
                await func.callback(e, ctx)
                handled = True
            else:
                handled = False

            await bot.on_crescent_error(e, ctx, handled)


def _get_command(
    bot: Bot,
    name: str,
    type: int,
    guild_id: Optional[Snowflake],
    group: Optional[str],
    sub_group: Optional[str],
) -> MetaStruct[CommandCallbackT, AppCommandMeta]:

    kwargs: Dict[str, Any] = dict(name=name, type=type, group=group, sub_group=sub_group)

    with suppress(KeyError):
        return bot._command_handler.registry[Unique(guild_id=guild_id, **kwargs)]
    with suppress(KeyError):
        return bot._command_handler.registry[Unique(guild_id=UNDEFINED, **kwargs)]
    raise CommandNotFoundError(f"Handler for command `{name}` does not exist locally.")


_VALUE_TYPE_LINK: Dict[OptionType | int, str] = {
    OptionType.ROLE: "roles",
    OptionType.USER: "users",
    OptionType.CHANNEL: "channels",
}


def _context_from_interaction_resp(interaction: CommandInteraction) -> Context:
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
            options = unwrap(option.options)[0].options

    callback_options: Mapping[str, OptionTypesT | Message | User]
    if interaction.command_type is CommandType.SLASH:
        callback_options = _options_to_kwargs(interaction, options)
    else:
        callback_options = _resolved_data_to_kwargs(interaction)

    return Context(
        app=cast("RestAndCacheAware", interaction.app),
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
        command_type=CommandType(interaction.command_type),
        options=callback_options,
    )


def _options_to_kwargs(
    interaction: CommandInteraction, options: Optional[Sequence[CommandInteractionOption]]
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
