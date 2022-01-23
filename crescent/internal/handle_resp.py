from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from hikari import CommandInteraction, CommandInteractionOption, OptionType
from crescent.context import Context
from crescent.internal.app_command import Unique
from crescent.mentionable import Mentionable
from crescent.utils.options import unwrap

if TYPE_CHECKING:
    from typing import Any, Dict, Sequence, cast
    from hikari import InteractionCreateEvent
    from crescent.bot import Bot


__all__: Sequence = (
    "handle_resp",
)


async def handle_resp(event: InteractionCreateEvent):

    interaction = event.interaction
    bot = event.app

    if TYPE_CHECKING:
        interaction = cast(CommandInteraction, interaction)
        bot = cast(Bot, bot)

    key = Unique(
        interaction.command_name,
        interaction.guild_id,
        None,
        None,
    )

    command = bot._command_handler.registry.get(key)

    options = _options_to_kwargs(interaction)

    ctx = Context._from_partial_interaction(interaction)

    await unwrap(command).callback(ctx, **options)

_VALUE_TYPE_LINK: Dict[OptionType | int, str] = {
    OptionType.ROLE: "roles",
    OptionType.USER: "users",
    OptionType.CHANNEL: "channels"
}


def _options_to_kwargs(interaction: CommandInteraction) -> Dict[str, Any]:
    if not interaction.options:
        return {}

    return {
        option.name: _extract_value(option, interaction) for option in interaction.options
    }


def _extract_value(option: CommandInteractionOption, interaction: CommandInteraction) -> Any:
    if option.type is OptionType.MENTIONABLE:
        return Mentionable._from_interaction(interaction)

    resolved_type: Optional[str] = _VALUE_TYPE_LINK.get(option.type)

    if resolved_type is None:
        return option.value

    resolved = getattr(interaction.resolved, resolved_type)
    return next(iter(resolved.values()))
