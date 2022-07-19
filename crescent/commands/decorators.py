from __future__ import annotations

from functools import partial
from inspect import isclass, isfunction
from typing import TYPE_CHECKING, Awaitable, Callable, cast, overload

from hikari import UNDEFINED, CommandOption, CommandType, Permissions, Snowflakeish, UndefinedType

from crescent.bot import Bot
from crescent.commands.options import ClassCommandOption
from crescent.commands.signature import gen_command_option, get_autocomplete_func
from crescent.internal.registry import register_command
from crescent.utils import get_parameters

if TYPE_CHECKING:
    from typing import Any, Sequence, TypeVar

    from crescent.internal.app_command import AppCommandMeta
    from crescent.internal.meta_struct import MetaStruct
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
    async def callback(*args: Any, **kwargs: Any) -> Any:
        values = defaults.copy()
        values.update(kwargs)

        if isinstance(args[0], Bot):
            args = args[1:]

        cmd = cls()
        for k, v in values.items():
            k = name_map.get(k, k)
            setattr(cmd, k, v)

        return await cmd.callback(*args)

    return callback


@overload
def command(
    callback: CommandCallbackT | type[ClassCommandProto], /
) -> MetaStruct[CommandCallbackT, AppCommandMeta]:
    ...


@overload
def command(
    *,
    guild: Snowflakeish | None = ...,
    name: str | None = ...,
    description: str | None = ...,
    default_member_permissions: UndefinedType | int | Permissions = ...,
    dm_enabled: bool = ...,
    deprecated: bool = ...,
) -> Callable[
    [CommandCallbackT | type[ClassCommandProto]], MetaStruct[CommandCallbackT, AppCommandMeta],
]:
    ...


def command(
    callback: CommandCallbackT | type[ClassCommandProto] | None = None,
    /,
    *,
    guild: Snowflakeish | None = None,
    name: str | None = None,
    description: str | None = None,
    default_member_permissions: UndefinedType | int | Permissions = UNDEFINED,
    dm_enabled: bool = True,
    deprecated: bool = False,
) -> MetaStruct[CommandCallbackT, AppCommandMeta] | Callable[
    [CommandCallbackT | type[ClassCommandProto]], MetaStruct[CommandCallbackT, AppCommandMeta],
]:
    if not callback:
        return partial(
            command,
            guild=guild,
            name=name,
            description=description,
            default_member_permissions=default_member_permissions,
            dm_enabled=dm_enabled,
            deprecated=deprecated,
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

        for param in get_parameters(callback_func):
            if param is None:
                continue

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
        command_type=CommandType.SLASH,
        name=name or callback.__name__,
        guild=guild,
        description=description or "No Description",
        options=options,
        default_member_permissions=default_member_permissions,
        dm_enabled=dm_enabled,
        deprecated=deprecated,
        autocomplete=autocomplete,
    )


def _kwargs_to_args_callback(
    callback: Callable[..., Awaitable[Any]]
) -> Callable[..., Awaitable[Any]]:
    async def inner(*args: Any, **kwargs: Any) -> Any:
        return await callback(*args, *kwargs.values())

    return inner


@overload
def user_command(
    callback: UserCommandCallbackT, /
) -> MetaStruct[UserCommandCallbackT, AppCommandMeta]:
    ...


@overload
def user_command(
    *,
    guild: Snowflakeish | None = ...,
    name: str | None = ...,
    default_member_permissions: UndefinedType | int | Permissions = ...,
    dm_enabled: bool = ...,
    deprecated: bool = ...,
) -> Callable[[UserCommandCallbackT], MetaStruct[UserCommandCallbackT, AppCommandMeta]]:
    ...


def user_command(
    callback: UserCommandCallbackT | None = None,
    /,
    *,
    guild: Snowflakeish | None = None,
    name: str | None = None,
    default_member_permissions: UndefinedType | int | Permissions = UNDEFINED,
    dm_enabled: bool = True,
    deprecated: bool = False,
) -> Callable[
    [UserCommandCallbackT], MetaStruct[UserCommandCallbackT, AppCommandMeta]
] | MetaStruct[UserCommandCallbackT, AppCommandMeta]:
    if not callback:
        return partial(
            user_command,
            guild=guild,
            name=name,
            default_member_permissions=default_member_permissions,
            dm_enabled=dm_enabled,
            deprecated=deprecated,
        )

    return register_command(
        callback=_kwargs_to_args_callback(callback),
        command_type=CommandType.USER,
        name=name or callback.__name__,
        guild=guild,
        default_member_permissions=default_member_permissions,
        dm_enabled=dm_enabled,
        deprecated=deprecated,
    )


@overload
def message_command(
    callback: MessageCommandCallbackT, /
) -> MetaStruct[MessageCommandCallbackT, AppCommandMeta]:
    ...


@overload
def message_command(
    *,
    guild: Snowflakeish | None = ...,
    name: str | None = ...,
    default_member_permissions: UndefinedType | int | Permissions = ...,
    dm_enabled: bool = ...,
    deprecated: bool = ...,
) -> Callable[[MessageCommandCallbackT], MetaStruct[MessageCommandCallbackT, AppCommandMeta]]:
    ...


def message_command(
    callback: MessageCommandCallbackT | None = None,
    /,
    *,
    guild: Snowflakeish | None = None,
    name: str | None = None,
    default_member_permissions: UndefinedType | int | Permissions = UNDEFINED,
    dm_enabled: bool = True,
    deprecated: bool = False,
) -> Callable[
    [MessageCommandCallbackT], MetaStruct[MessageCommandCallbackT, AppCommandMeta],
] | MetaStruct[MessageCommandCallbackT, AppCommandMeta]:
    if not callback:
        return partial(
            message_command,
            guild=guild,
            name=name,
            default_member_permissions=default_member_permissions,
            dm_enabled=dm_enabled,
            deprecated=deprecated,
        )

    return register_command(
        callback=_kwargs_to_args_callback(callback),
        command_type=CommandType.MESSAGE,
        name=name or callback.__name__,
        guild=guild,
        default_member_permissions=default_member_permissions,
        dm_enabled=dm_enabled,
        deprecated=deprecated,
    )
