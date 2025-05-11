from __future__ import annotations

from asyncio import Task, create_task
from functools import partial, wraps
from inspect import isawaitable, isclass, isfunction
from typing import TYPE_CHECKING, Awaitable, Callable, Iterable, cast, overload

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

from crescent.commands.options import ClassCommandOption
from crescent.exceptions import ConverterExceptionMeta, ConverterExceptions
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
    cls: type[ClassCommandProto],
    defaults: dict[str, Any],
    name_map: dict[str, str],
    converters: dict[str, Callable[[Any], Any]],
) -> CommandCallbackT:
    @wraps(cls.callback)
    async def callback(*args: Any, **kwargs: Any) -> Any:
        values = defaults.copy()
        values.update(kwargs)

        cmd = cls()

        async def set_later(key: str, value: object | Awaitable[object]) -> None:
            if isawaitable(value):
                value = await value
            setattr(cmd, key, value)

        errors: list[ConverterExceptionMeta] = []
        tasks: list[tuple[Task[None], str, Any]] = []
        # [(Task, option key, raw value)]

        for key, raw_val in values.items():
            # val: The converted (if a converter existed) value
            # raw_val: The original value passed by Discord
            # key: The key of the option on the class
            # name: The name of the option used by Discord

            key = name_map.get(key, key)

            if conv := converters.get(key):
                try:
                    val = conv(raw_val)
                except Exception as e:
                    errors.append(ConverterExceptionMeta(cls, key, raw_val, e))
                    continue
            else:
                val = raw_val

            tasks.append((create_task(set_later(key, val)), key, raw_val))

        for t, key, raw_val in tasks:
            try:
                await t
            except Exception as e:
                errors.append(ConverterExceptionMeta(cls, key, raw_val, e))

        if errors:
            raise ConverterExceptions(errors)

        return await cmd.callback(*args)

    return callback


@overload
def command(
    callback: CommandCallbackT | type[ClassCommandProto], /
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
        )  # pyright: ignore

    autocomplete: dict[str, AutocompleteCallbackT[Any]] = {}
    options: list[CommandOption] = []

    if isclass(callback):
        # If callback is a class it must be `type[ClassCommandProto]` because of the function
        # signature.
        callback = cast("type[ClassCommandProto]", callback)

        name_map: dict[str, str] = {}
        defaults: dict[str, Any] = {}
        converters: dict[str, Callable[[Any], Any]] = {}

        for n, v in callback.__dict__.items():
            if not isinstance(v, ClassCommandOption):
                continue

            if TYPE_CHECKING:
                v = cast("ClassCommandOption[Any, Any]", v)  # type: ignore[redundant-cast]

            generated = v._gen_option(n)
            options.append(generated)

            if v.autocomplete:
                autocomplete[generated.name] = v.autocomplete

            if v.converter:
                converters[generated.name] = v.converter

            if generated.name != n:
                name_map[generated.name] = n

            defaults[generated.name] = v.default

        callback_func = _class_command_callback(callback, defaults, name_map, converters)

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
        )  # pyright: ignore

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
        )  # pyright: ignore

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
