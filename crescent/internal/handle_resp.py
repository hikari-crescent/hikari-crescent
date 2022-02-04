from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING, Optional

from hikari import UNDEFINED, CommandInteraction, Snowflake

from crescent.context import Context
from crescent.exceptions import CommandNotFoundError
from crescent.internal.app_command import Unique
from crescent.utils.gather_iter import gather_iter

if TYPE_CHECKING:
    from typing import Any, Dict, Sequence, cast

    from hikari import InteractionCreateEvent

    from crescent.bot import Bot
    from crescent.internal import AppCommandMeta, MetaStruct
    from crescent.typedefs import CommandCallbackT


__all__: Sequence = ("handle_resp",)


async def handle_resp(event: InteractionCreateEvent):

    interaction = event.interaction
    bot = event.app

    if TYPE_CHECKING:
        interaction = cast(CommandInteraction, interaction)
        bot = cast(Bot, bot)

    ctx = Context._from_command_interaction(interaction)
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
            if hdlrs := command.app._error_handler.registry.get(e.__class__):
                await gather_iter(func.callback(exc=e, ctx=ctx) for func in hdlrs)
            else:
                raise


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
