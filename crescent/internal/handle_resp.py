from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from hikari import CommandInteraction, CommandInteractionOption, OptionType

from crescent.context import Context
from crescent.internal.app_command import AppCommandType, Unique
from crescent.mentionable import Mentionable
from crescent.utils.options import unwrap

if TYPE_CHECKING:
    from typing import Any, Dict, Sequence, cast

    from hikari import InteractionCreateEvent

    from crescent.bot import Bot


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

    command = bot._command_handler.registry[
        Unique(
            name=name,
            type=AppCommandType.CHAT_INPUT,
            guild_id=interaction.guild_id,
            group=group,
            sub_group=sub_group,
        )
    ]

    ctx = Context._from_command_interaction(interaction)
    callback_params = _options_to_kwargs(interaction, options)

    args: List[Any] = [ctx]
    if command.is_method:
        args.insert(0, command.manager)

    await command.callback(*args, **callback_params)


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


def _extract_value(
    option: CommandInteractionOption, interaction: CommandInteraction
) -> Any:
    if option.type is OptionType.MENTIONABLE:
        return Mentionable._from_interaction(interaction)

    resolved_type: Optional[str] = _VALUE_TYPE_LINK.get(option.type)

    if resolved_type is None:
        return option.value

    resolved = getattr(interaction.resolved, resolved_type)
    return next(iter(resolved.values()))
