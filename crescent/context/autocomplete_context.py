from __future__ import annotations

from typing import Any, Callable, Sequence

from hikari import (
    AutocompleteInteraction,
    CommandInteractionOption,
    Member,
    NotFoundError,
    OptionType,
    PartialChannel,
    Role,
    Snowflake,
    User,
)
from hikari.traits import CacheAware

from crescent.context.base_context import BaseContext
from crescent.mentionable import Mentionable
from crescent.utils import gather_iter

__all__: Sequence[str] = ("AutocompleteContext",)


async def _fetch_user(ctx: AutocompleteContext, value: Snowflake) -> User | Member:
    if isinstance(ctx.app, CacheAware):
        if ctx.guild_id:
            if member := ctx.app.cache.get_member(ctx.guild_id, value):
                return member
        else:
            if user := ctx.app.cache.get_user(value):
                return user

    if ctx.guild_id:
        return await ctx.app.rest.fetch_member(ctx.guild_id, value)
    else:
        return await ctx.app.rest.fetch_user(value)


async def _fetch_role(ctx: AutocompleteContext, value: Snowflake) -> Role:
    assert ctx.guild_id

    if isinstance(ctx.app, CacheAware):
        if role := ctx.app.cache.get_role(value):
            return role

    roles = await ctx.app.rest.fetch_roles(ctx.guild_id)
    return next(filter(lambda r: r.id == value, roles))


async def _fetch_mentionable(ctx: AutocompleteContext, value: Snowflake) -> Mentionable:
    try:
        user = await _fetch_user(ctx, value)
    except NotFoundError:
        user = None

    if not user:
        try:
            role = await _fetch_role(ctx, value)
        except NotFoundError:
            role = None
    else:
        role = None

    return Mentionable(user, role)


async def _fetch_channel(ctx: AutocompleteContext, value: Snowflake) -> PartialChannel:
    if isinstance(ctx.app, CacheAware):
        if channel := ctx.app.cache.get_guild_channel(value):
            return channel

    return await ctx.app.rest.fetch_channel(value)


async def _fetch_attachment(*_: Any) -> None:
    return None


_serialization_map: dict[OptionType, Callable[[AutocompleteContext, Snowflake], Any]] = {
    OptionType.USER: _fetch_user,
    OptionType.ROLE: _fetch_role,
    OptionType.MENTIONABLE: _fetch_mentionable,
    OptionType.CHANNEL: _fetch_channel,
    OptionType.ATTACHMENT: _fetch_attachment,
}


class AutocompleteContext(BaseContext):
    """Represents the context for autocomplete interactions"""

    __slots__ = ("interaction",)

    interaction: AutocompleteInteraction

    async def fetch_options(self) -> dict[str, Any]:
        if not self.interaction.options:
            return {}

        out: dict[str, Any] = {}

        async def get_option(option: CommandInteractionOption) -> None:
            if func := _serialization_map.get(OptionType(option.type)):
                # `option.value` is a `Snowflake` or `int` for all option types
                # in `_serialization_map`.
                assert option.value
                out[option.name] = await func(self, Snowflake(option.value))
            else:
                out[option.name] = option.value

        await gather_iter(get_option(option) for option in self.interaction.options)

        return out
