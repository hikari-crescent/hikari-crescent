from __future__ import annotations

from contextlib import suppress
from copy import copy
from typing import TYPE_CHECKING, Optional

from hikari import (
    UNDEFINED,
    CommandInteraction,
    CommandInteractionOption,
    OptionType,
    Snowflake,
)

from crescent.context import Context
from crescent.exceptions import CommandNotFoundError
from crescent.internal.app_command import AppCommandType, Unique
from crescent.mentionable import Mentionable
from crescent.utils.options import unwrap

if TYPE_CHECKING:
    from typing import Any, Dict, Sequence, cast

    from hikari import InteractionCreateEvent

    from crescent.bot import Bot
    from crescent.internal import AppCommandMeta, MetaStruct
    from crescent.typedefs import CommandCallback


__all__: Sequence = ("handle_resp",)


async def handle_resp(event: InteractionCreateEvent):

    interaction = event.interaction
    bot = event.app

    if TYPE_CHECKING:
        interaction = cast(CommandInteraction, interaction)
        bot = cast(Bot, bot)

    name: str = interaction.command_name
    group: Optional[str] = None
    sub_group: Optional[str] = None
    options: Optional[Sequence[CommandInteractionOption]] = interaction.options

    if options:
        option = unwrap(options)[0]
        if option.type == 1:
            group = name
            name = option.name
            options = option.options
        elif option.type == 2:
            group = interaction.command_name
            sub_group = option.name
            name = unwrap(option.options)[0].name
            options = unwrap(option.options)[0].options

    command = _get_command(bot, name, interaction.guild_id, group, sub_group)
    ctx = Context._from_command_interaction(interaction)
    callback_options = _options_to_kwargs(interaction, options)

    for hook in command.interaction_hooks:
        hook_res = await hook(ctx, copy(callback_options))

        if hook_res:
            if hook_res.options:
                callback_options = hook_res.options

            if hook_res.exit:
                break

    else:
        await command.callback(ctx, **callback_options)


def _get_command(
    bot: Bot,
    name: str,
    guild_id: Optional[Snowflake],
    group: Optional[str],
    sub_group: Optional[str],
) -> MetaStruct[CommandCallback, AppCommandMeta]:

    kwargs: Dict[str, Any] = dict(
        name=name,
        type=AppCommandType.CHAT_INPUT,
        group=group,
        sub_group=sub_group,
    )

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
    return next(iter(resolved.values()))
