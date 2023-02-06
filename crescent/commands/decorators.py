from __future__ import annotations

from functools import partial, wraps
from inspect import isclass, isfunction
from typing import TYPE_CHECKING, Awaitable, Callable, cast, overload

from hikari import UNDEFINED, CommandOption, CommandType, Permissions, Snowflakeish, UndefinedType
from sigparse import sigparse

from crescent.commands.options import ClassCommandOption
from crescent.commands.signature import gen_command_option, get_autocomplete_func
from crescent.internal.registry import register_command
from crescent.locale import LocaleBuilder

if TYPE_CHECKING:
    from typing import Any, Sequence, TypeVar

    from crescent.internal.app_command import AppCommandMeta
    from crescent.internal.includable import Includable
    from crescent.typedefs import (
        AutocompleteCallbackT,
        ClassCommandProto,
        CommandCallbackT,
        MessageCommandCallbackT,
        UserCommandCallbackT,
    )

    T = TypeVar("T")

__all__: Sequence[str] = ("command", "user_command", "message_command")


def _class_command_callback(
    cls: type[ClassCommandProto], defaults: dict[str, Any], name_map: dict[str, str]
) -> CommandCallbackT:
    @wraps(cls.callback)
    async def callback(*args: Any, **kwargs: Any) -> Any:
        values = defaults.copy()
        values.update(kwargs)

        cmd = cls()
        for k, v in values.items():
            k = name_map.get(k, k)
            setattr(cmd, k, v)

        return await cmd.callback(*args)

    return callback


@overload
def command(callback: CommandCallbackT | type[ClassCommandProto], /) -> Includable[AppCommandMeta]:
    ...


@overload
def command(
    *,
    guild: Snowflakeish | None = ...,
    name: str | LocaleBuilder | None = ...,
    description: str | LocaleBuilder | None = ...,
    default_member_permissions: UndefinedType | int | Permissions = ...,
    dm_enabled: bool = ...,
    nsfw: bool | None = ...,
) -> Callable[[CommandCallbackT | type[ClassCommandProto]], Includable[AppCommandMeta]]:
    ...


def command(
    callback: CommandCallbackT | type[ClassCommandProto] | None = None,
    /,
    *,
    guild: Snowflakeish | None = None,
    name: str | LocaleBuilder | None = None,
    description: str | LocaleBuilder | None = None,
    default_member_permissions: UndefinedType | int | Permissions = UNDEFINED,
    dm_enabled: bool = True,
    nsfw: bool | None = None,
) -> (
    Includable[AppCommandMeta]
    | Callable[[CommandCallbackT | type[ClassCommandProto]], Includable[AppCommandMeta]]
):
    if not callback:
        return partial(
            command,
            guild=guild,
            name=name,
            description=description,
            default_member_permissions=default_member_permissions,
            dm_enabled=dm_enabled,
            nsfw=nsfw,
        )

    autocomplete: dict[str, AutocompleteCallbackT] = {}
    options: list[CommandOption] = []

    if isclass(callback):
        # If callback is a class it must be `type[ClassCommandProto]` because of the function
        # signature.
        callback = cast("type[ClassCommandProto]", callback)

        name_map: dict[str, str] = {}
        defaults: dict[str, Any] = {}

        for n, v in callback.__dict__.items():
            if not isinstance(v, ClassCommandOption):
                continue

            generated = v._gen_option(n)
            options.append(generated)

            if v.autocomplete:
                autocomplete[generated.name] = v.autocomplete

            if generated.name != n:
                name_map[generated.name] = n

            defaults[generated.name] = v.default

        callback_func = _class_command_callback(callback, defaults, name_map)

    elif isfunction(callback):
        callback_func = callback

        for param in sigparse(callback_func).parameters:
            option = gen_command_option(param)
            if not option:
                continue

            options.append(option)

            if autocomplete_func := get_autocomplete_func(param):
                autocomplete[option.name] = autocomplete_func

    else:
        raise NotImplementedError("This function only works with classes and functions")

    return register_command(
        callback=callback_func,
        owner=callback,
        command_type=CommandType.SLASH,
        name=name or callback.__name__,
        guild=guild,
        description=description or "No Description",
        options=options,
        default_member_permissions=default_member_permissions,
        dm_enabled=dm_enabled,
        autocomplete=autocomplete,
        nsfw=nsfw,
    )


def _kwargs_to_args_callback(
    callback: Callable[..., Awaitable[Any]]
) -> Callable[..., Awaitable[Any]]:
    @wraps(callback)
    async def inner(*args: Any, **kwargs: Any) -> Any:
        return await callback(*args, *kwargs.values())

    return inner


@overload
def user_command(callback: UserCommandCallbackT, /) -> Includable[AppCommandMeta]:
    ...


@overload
def user_command(
    *,
    guild: Snowflakeish | None = ...,
    name: str | None = ...,
    default_member_permissions: UndefinedType | int | Permissions = ...,
    dm_enabled: bool = ...,
    nsfw: bool | None = ...,
) -> Callable[[UserCommandCallbackT], Includable[AppCommandMeta]]:
    ...


def user_command(
    callback: UserCommandCallbackT | None = None,
    /,
    *,
    guild: Snowflakeish | None = None,
    name: str | None = None,
    default_member_permissions: UndefinedType | int | Permissions = UNDEFINED,
    dm_enabled: bool = True,
    nsfw: bool | None = None,
) -> Callable[[UserCommandCallbackT], Includable[AppCommandMeta]] | Includable[AppCommandMeta]:
    if not callback:
        return partial(
            user_command,
            guild=guild,
            name=name,
            default_member_permissions=default_member_permissions,
            dm_enabled=dm_enabled,
            nsfw=nsfw,
        )

    return register_command(
        callback=_kwargs_to_args_callback(callback),
        owner=callback,
        command_type=CommandType.USER,
        name=name or callback.__name__,
        guild=guild,
        default_member_permissions=default_member_permissions,
        dm_enabled=dm_enabled,
        nsfw=nsfw,
    )


@overload
def message_command(callback: MessageCommandCallbackT, /) -> Includable[AppCommandMeta]:
    ...


@overload
def message_command(
    *,
    guild: Snowflakeish | None = ...,
    name: str | None = ...,
    default_member_permissions: UndefinedType | int | Permissions = ...,
    dm_enabled: bool = ...,
    nsfw: bool | None = ...,
) -> Callable[[MessageCommandCallbackT], Includable[AppCommandMeta]]:
    ...


def message_command(
    callback: MessageCommandCallbackT | None = None,
    /,
    *,
    guild: Snowflakeish | None = None,
    name: str | None = None,
    default_member_permissions: UndefinedType | int | Permissions = UNDEFINED,
    dm_enabled: bool = True,
    nsfw: bool | None = None,
) -> Callable[[MessageCommandCallbackT], Includable[AppCommandMeta]] | Includable[AppCommandMeta]:
    if not callback:
        return partial(
            message_command,
            guild=guild,
            name=name,
            default_member_permissions=default_member_permissions,
            dm_enabled=dm_enabled,
            nsfw=nsfw,
        )

    return register_command(
        callback=_kwargs_to_args_callback(callback),
        owner=callback,
        command_type=CommandType.MESSAGE,
        name=name or callback.__name__,
        guild=guild,
        default_member_permissions=default_member_permissions,
        dm_enabled=dm_enabled,
        nsfw=nsfw,
    )
