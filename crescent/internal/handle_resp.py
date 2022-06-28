from __future__ import annotations

from contextlib import suppress
from logging import getLogger
from typing import TYPE_CHECKING, Mapping, cast

from hikari import (
    UNDEFINED,
    AutocompleteInteraction,
    AutocompleteInteractionOption,
    CommandType,
    InteractionType,
    OptionType,
    Snowflake,
)

from crescent.context import Context
from crescent.internal.app_command import Unique
from crescent.mentionable import Mentionable
from crescent.utils import unwrap

if TYPE_CHECKING:
    from typing import Any, Sequence

    from hikari import (
        CommandInteraction,
        CommandInteractionOption,
        InteractionCreateEvent,
        Message,
        User,
    )

    from crescent.bot import Bot
    from crescent.internal import AppCommandMeta, MetaStruct
    from crescent.typedefs import CommandCallbackT, HookCallbackT, OptionTypesT


_log = getLogger(__name__)

__all__: Sequence[str] = ("handle_resp",)


async def handle_resp(event: InteractionCreateEvent) -> None:
    interaction = event.interaction
    bot = event.app

    if interaction.type is InteractionType.MESSAGE_COMPONENT:
        return

    if TYPE_CHECKING:
        interaction = cast(CommandInteraction, interaction)
        bot = cast(Bot, bot)

    ctx = _context_from_interaction_resp(interaction)

    command = _get_command(
        bot, ctx.command, int(ctx.command_type), ctx.guild_id, ctx.group, ctx.sub_group
    )

    if not command:
        if not bot.allow_unknown_interactions:
            _log.warning(
                f"Handler for command `{ctx.command}` does not exist locally. (If this is"
                " intended, add `allow_unknown_interactions=True` to the Bot's constructor.)"
            )
        return

    if interaction.type is InteractionType.AUTOCOMPLETE:
        await _handle_autocomplete_resp(command, ctx)
        return

    await _handle_slash_resp(bot, command, ctx)


async def _handle_hooks(hooks: Sequence[HookCallbackT], ctx: Context) -> bool:
    """Returns `False` if the command should not be run."""
    for hook in hooks:
        hook_res = await hook(ctx)

        if hook_res and hook_res.exit:
            return False
    return True


async def _handle_slash_resp(
    bot: Bot, command: MetaStruct[CommandCallbackT, AppCommandMeta], ctx: Context
) -> None:

    if not await _handle_hooks(command.metadata.hooks, ctx):
        return

    try:
        await command.callback(ctx, **ctx.options)
        await _handle_hooks(command.metadata.after_hooks, ctx)
    except Exception as exc:
        handled = await command.app._command_error_handler.try_handle(exc, [exc, ctx])
        await bot.on_crescent_command_error(exc, ctx, handled)


async def _handle_autocomplete_resp(
    command: MetaStruct[CommandCallbackT, AppCommandMeta], ctx: Context
) -> None:
    interaction = cast(AutocompleteInteraction, ctx.interaction)

    if not command.metadata.autocomplete:
        return

    option = _get_option_recursive(interaction.options)
    if not option:
        return
    autocomplete = command.metadata.autocomplete[option.name]

    try:
        await interaction.create_response(await autocomplete(ctx, option))
    except Exception as exc:
        handled = await command.app._autocomplete_error_handler.try_handle(exc, [exc, ctx, option])
        await command.app.on_crescent_autocomplete_error(exc, ctx, option, handled)


def _get_option_recursive(
    options: Sequence[AutocompleteInteractionOption],
) -> AutocompleteInteractionOption | None:
    for option in options:
        if option.is_focused:
            return option
        if not option.options:
            continue
        if maybe_option := _get_option_recursive(option.options):
            return maybe_option
    return None


def _get_command(
    bot: Bot,
    name: str,
    type: int,
    guild_id: Snowflake | None,
    group: str | None,
    sub_group: str | None,
) -> MetaStruct[CommandCallbackT, AppCommandMeta] | None:

    kwargs: dict[str, Any] = dict(name=name, type=type, group=group, sub_group=sub_group)

    with suppress(KeyError):
        return bot._command_handler.registry[Unique(guild_id=guild_id, **kwargs)]
    with suppress(KeyError):
        return bot._command_handler.registry[Unique(guild_id=UNDEFINED, **kwargs)]
    return None


_VALUE_TYPE_LINK: dict[OptionType | int, str] = {
    OptionType.ROLE: "roles",
    OptionType.USER: "users",
    OptionType.CHANNEL: "channels",
    OptionType.ATTACHMENT: "attachments",
}


def _context_from_interaction_resp(interaction: CommandInteraction) -> Context:
    name: str = interaction.command_name
    group: str | None = None
    sub_group: str | None = None
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
        interaction=interaction,
        app=cast("Bot", interaction.app),
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
    interaction: CommandInteraction, options: Sequence[CommandInteractionOption] | None
) -> dict[str, Any]:
    if not options:
        return {}

    return {option.name: _extract_value(option, interaction) for option in options}


def _extract_value(option: CommandInteractionOption, interaction: CommandInteraction) -> Any:
    if option.type is OptionType.MENTIONABLE:
        return Mentionable._from_interaction(interaction)

    resolved_type: str | None = _VALUE_TYPE_LINK.get(option.type)

    if resolved_type is None:
        return option.value

    resolved = getattr(interaction.resolved, resolved_type, None)

    # `option.value` is guaranteed to have a value because this is not a command group.
    assert option.value is not None

    # `resolved` is None when an autocomplete command has a user or role as a previous option.
    # This should be refactored out in the autocomplete rewrite for 1.0.0
    if resolved is None:
        return Snowflake(option.value)
    return resolved[option.value]


def _resolved_data_to_kwargs(interaction: CommandInteraction) -> dict[str, Message | User]:
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
