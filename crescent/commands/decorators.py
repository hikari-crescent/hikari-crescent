from __future__ import annotations

from asyncio import Task, create_task
from functools import partial, wraps
from inspect import isawaitable, isclass, isfunction
from typing import TYPE_CHECKING, Any, cast, overload

from hikari import (
    UNDEFINED,
    ApplicationContextType,
    CommandOption,
    CommandType,
    Permissions,
    Snowflakeish,
    UndefinedOr,
    UndefinedType,
)

from crescent.commands.options import ClassCommandOption, _ChoiceOption
from crescent.exceptions import ConverterExceptionMeta, ConverterExceptions
from crescent.internal.registry import register_command

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Iterable

    from crescent.internal.app_command import AppCommandMeta
    from crescent.internal.includable import Includable
    from crescent.locale import LocaleBuilder
    from crescent.typedefs import (
        AutocompleteCallbackT,
        ClassCommandProto,
        CommandCallbackT,
        MessageCommandCallbackT,
        UserCommandCallbackT,
    )

__all__ = ("command", "message_command", "user_command")


def _class_command_callback(
    cls: type[ClassCommandProto],
    defaults: dict[str, Any],
    name_to_field: dict[str, str],
    converters: dict[str, Callable[[Any], Any]],
) -> CommandCallbackT:
    @wraps(cls.callback)
    async def callback(*args: Any, **kwargs: Any) -> Any:
        cmd = cls()

        for name, value in defaults.items():
            if name in kwargs:
                continue

            setattr(cmd, name_to_field.get(name, name), value)

        async def set_later(field: str, value: Awaitable[object]) -> None:
            setattr(cmd, field, await value)

        errors: list[ConverterExceptionMeta] = []
        tasks: list[tuple[Task[None], str, object]] = []
        # [(task, field, raw value)]

        for name, raw_val in kwargs.items():
            field = name_to_field.get(name, name)

            if (converter := converters.get(name)) is not None:
                try:
                    val = converter(raw_val)
                except Exception as e:
                    errors.append(ConverterExceptionMeta(cls, field, raw_val, e))
                    continue
            else:
                val = raw_val

            if isawaitable(val):
                tasks.append((create_task(set_later(field, val)), field, raw_val))
            else:
                setattr(cmd, field, val)

        # TODO: can we gather these tasks?
        for task, field, raw_val in tasks:
            try:
                await task
            except Exception as e:
                errors.append(ConverterExceptionMeta(cls, field, raw_val, e))

        if errors:
            raise ConverterExceptions(errors)

        return await cmd.callback(*args)

    return callback


@overload
def command(
    callback: CommandCallbackT | type[ClassCommandProto],
    /,
) -> Includable[AppCommandMeta]: ...


@overload
def command(
    *,
    guild: Snowflakeish | None = ...,
    name: str | LocaleBuilder | None = ...,
    description: str | LocaleBuilder | None = ...,
    default_member_permissions: UndefinedType | int | Permissions = ...,
    context_types: UndefinedOr[Iterable[ApplicationContextType]] = ...,
    nsfw: bool | None = ...,
) -> Callable[[CommandCallbackT | type[ClassCommandProto]], Includable[AppCommandMeta]]: ...


def command(
    callback: CommandCallbackT | type[ClassCommandProto] | None = None,
    /,
    *,
    guild: Snowflakeish | None = None,
    name: str | LocaleBuilder | None = None,
    description: str | LocaleBuilder | None = None,
    default_member_permissions: UndefinedType | int | Permissions = UNDEFINED,
    context_types: UndefinedOr[Iterable[ApplicationContextType]] = UNDEFINED,
    nsfw: bool | None = None,
) -> (
    Includable[AppCommandMeta]
    | Callable[[CommandCallbackT | type[ClassCommandProto]], Includable[AppCommandMeta]]
):
    """
    Register a slash command.

    ### Example
    ```python
    import hikari
    import crescent

    bot = hikari.GatewayBot("YOUR_TOKEN_HERE")
    client = crescent.Client(bot)

    @client.include
    @crescent.command
    async def ping(ctx: crescent.Context):
        await ctx.respond("Pong")
    ```

    Args:
        name:
            The name of this command. If not specified the function name will
            be used.
        description:
            The description of this command. If not specified the description
            will be set to "No Description".
        guild:
            The guild to register this command to. If not specified this
            command will be registered globally.
        default_member_permissions:
            The default permissions for this command. For more information see
            [the discord api docs](https://discord.com/developers/docs/topics/permissions)
            and [the hikari docs](https://docs.hikari-py.dev/en/latest/reference/hikari/permissions/).
        context_types:
            The contexts in which the command can be used. Defaults to all.
        nsfw:
            Set to `True` to mark this command as nsfw. Defaults to `None`.
    """
    if not callback:
        return partial(
            command,
            guild=guild,
            name=name,
            description=description,
            default_member_permissions=default_member_permissions,
            context_types=context_types,
            nsfw=nsfw,
        )  # pyright: ignore[reportReturnType]

    autocomplete: dict[str, AutocompleteCallbackT[Any]] = {}
    options: list[CommandOption] = []

    if isclass(callback):
        # If callback is a class it must be `type[ClassCommandProto]` because of the function
        # signature.
        callback = cast("type[ClassCommandProto]", callback)

        name_to_field: dict[str, str] = {}
        defaults: dict[str, Any] = {}
        converters: dict[str, Callable[[Any], Any]] = {}

        for field, value in callback.__dict__.items():
            if not isinstance(value, ClassCommandOption):
                continue

            option = cast("ClassCommandOption[Any, object, object]", value)
            generated = option._gen_option(field)
            options.append(generated)

            if isinstance(option, _ChoiceOption) and option.autocomplete is not None:
                autocomplete[generated.name] = option.autocomplete

            if option.converter is not None:
                converters[generated.name] = option.converter

            name_to_field[generated.name] = field
            defaults[generated.name] = option.default

        callback_func = _class_command_callback(callback, defaults, name_to_field, converters)

    elif isfunction(callback):
        callback_func = callback
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
        context_types=context_types,
        autocomplete=autocomplete,
        nsfw=nsfw,
    )


def _kwargs_to_args_callback(
    callback: Callable[..., Awaitable[Any]],
) -> Callable[..., Awaitable[Any]]:
    @wraps(callback)
    async def inner(*args: Any, **kwargs: Any) -> Any:
        return await callback(*args, *kwargs.values())

    return inner


@overload
def user_command(callback: UserCommandCallbackT, /) -> Includable[AppCommandMeta]: ...


@overload
def user_command(
    *,
    guild: Snowflakeish | None = ...,
    name: str | None = ...,
    default_member_permissions: UndefinedType | int | Permissions = ...,
    context_types: UndefinedOr[list[ApplicationContextType]] = ...,
    nsfw: bool | None = ...,
) -> Callable[[UserCommandCallbackT], Includable[AppCommandMeta]]: ...


def user_command(
    callback: UserCommandCallbackT | None = None,
    /,
    *,
    guild: Snowflakeish | None = None,
    name: str | None = None,
    default_member_permissions: UndefinedType | int | Permissions = UNDEFINED,
    context_types: UndefinedOr[list[ApplicationContextType]] = UNDEFINED,
    nsfw: bool | None = None,
) -> Callable[[UserCommandCallbackT], Includable[AppCommandMeta]] | Includable[AppCommandMeta]:
    """
    Register a user command. A user command can be used by right clicking on a discord
    user. Your bot can have up to 5 user commands.

    ### Example
    ```python
    import hikari
    import crescent

    bot = hikari.GatewayBot("YOUR_TOKEN_HERE")
    client = crescent.Client(bot)

    @client.include
    @crescent.user_command
    async def ping(ctx: crescent.Context, user: hikari.User):
        await ctx.respond(user.username)
    ```

    Args:
        name:
            The name of this command. If not specified the function name will
            be used.
        guild:
            The guild to register this command to. If not specified this
            command will be registered globally.
        default_member_permissions:
            The default permissions for this command. For more information see
            [the discord api docs](https://discord.com/developers/docs/topics/permissions)
            and [the hikari docs](https://docs.hikari-py.dev/en/latest/reference/hikari/permissions/).
        context_types:
            The contexts in which the command can be used. Defaults to all.
        nsfw:
            Set to `True` to mark this command as nsfw. Defaults to `None`.
    """
    if not callback:
        return partial(
            user_command,
            guild=guild,
            name=name,
            default_member_permissions=default_member_permissions,
            context_types=context_types,
            nsfw=nsfw,
        )  # pyright: ignore[reportReturnType]

    return register_command(
        callback=_kwargs_to_args_callback(callback),
        owner=callback,
        command_type=CommandType.USER,
        name=name or callback.__name__,
        guild=guild,
        default_member_permissions=default_member_permissions,
        context_types=context_types,
        nsfw=nsfw,
    )


@overload
def message_command(callback: MessageCommandCallbackT, /) -> Includable[AppCommandMeta]: ...


@overload
def message_command(
    *,
    guild: Snowflakeish | None = ...,
    name: str | None = ...,
    default_member_permissions: UndefinedType | int | Permissions = ...,
    context_types: UndefinedOr[list[ApplicationContextType]] = ...,
    nsfw: bool | None = ...,
) -> Callable[[MessageCommandCallbackT], Includable[AppCommandMeta]]: ...


def message_command(
    callback: MessageCommandCallbackT | None = None,
    /,
    *,
    guild: Snowflakeish | None = None,
    name: str | None = None,
    default_member_permissions: UndefinedType | int | Permissions = UNDEFINED,
    context_types: UndefinedOr[list[ApplicationContextType]] = UNDEFINED,
    nsfw: bool | None = None,
) -> Callable[[MessageCommandCallbackT], Includable[AppCommandMeta]] | Includable[AppCommandMeta]:
    """
    Register a message command. A message command can be used by right clicking on a discord
    message. Your bot can have up to 5 message commands.

    ### Example
    ```python
    import hikari
    import crescent

    bot = hikari.GatewayBot("YOUR_TOKEN_HERE")
    client = crescent.Client(bot)

    @client.include
    @crescent.message_command
    async def ping(ctx: crescent.Context, message: hikari.Message):
        await ctx.respond(message.contents)
    ```

    Args:
        name:
            The name of this command. If not specified the function name will
            be used.
        guild:
            The guild to register this command to. If not specified this
            command will be registered globally.
        default_member_permissions:
            The default permissions for this command. For more information see
            [the discord api docs](https://discord.com/developers/docs/topics/permissions)
            and [the hikari docs](https://docs.hikari-py.dev/en/latest/reference/hikari/permissions/).
        context_types:
            The contexts in which the command can be used. Defaults to all.
        nsfw:
            Set to `True` to mark this command as nsfw. Defaults to `None`.
    """
    if not callback:
        return partial(
            message_command,
            guild=guild,
            name=name,
            default_member_permissions=default_member_permissions,
            context_types=context_types,
            nsfw=nsfw,
        )  # pyright: ignore[reportReturnType]

    return register_command(
        callback=_kwargs_to_args_callback(callback),
        owner=callback,
        command_type=CommandType.MESSAGE,
        name=name or callback.__name__,
        guild=guild,
        default_member_permissions=default_member_permissions,
        context_types=context_types,
        nsfw=nsfw,
    )
