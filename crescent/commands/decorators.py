from __future__ import annotations

from functools import partial
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    Dict,
    Type,
    Union,
    get_args,
    get_origin,
    overload,
)

from hikari import CommandOption, CommandType, OptionType, Snowflakeish

from crescent.bot import Bot
from crescent.commands.args import (
    Arg,
    ChannelTypes,
    Choices,
    Description,
    MaxValue,
    MinValue,
    Name,
)
from crescent.commands.options import OPTIONS_TYPE_MAP, ClassCommandOption, get_channel_types
from crescent.context import Context
from crescent.internal.registry import register_command
from crescent.utils import get_parameters

if TYPE_CHECKING:
    from inspect import Parameter
    from typing import Any, Optional, Sequence, TypeVar

    from crescent.internal.app_command import AppCommandMeta
    from crescent.internal.meta_struct import MetaStruct
    from crescent.typedefs import (
        ClassCommandProto,
        CommandCallbackT,
        MessageCommandCallbackT,
        UserCommandCallbackT,
    )

    T = TypeVar("T")

__all__: Sequence[str] = ("command", "user_command", "message_command")


NoneType = type(None)


def _unwrap_optional(origin: Type[Any]) -> Any:
    if get_origin(origin) is not Union:
        return origin

    args = get_args(origin)

    if len(args) != 2 or NoneType not in args:
        raise ValueError("Typehint must be `T`, `Optional[T]`, or `Union[T, None]`")

    if args[1] is NoneType:
        return args[0]

    return args[1]


def _gen_command_option(param: Parameter) -> Optional[CommandOption]:
    name = param.name
    typehint = param.annotation

    metadata = ()

    origin = _unwrap_optional(typehint)

    if hasattr(origin, "__metadata__"):
        metadata = origin.__metadata__
        origin = _unwrap_optional(origin.__origin__)

    if origin is Context or origin is param.empty:
        return None

    _type = OPTIONS_TYPE_MAP.get(origin)

    _channel_types = get_channel_types(origin)
    if _channel_types:
        _type = OptionType.CHANNEL

    if _type is None:
        raise ValueError(
            f"`{origin.__name__}` is not a valid typehint."
            " Must be `str`, `bool`, `int`, `float`, `hikari.PartialChannel`,"
            " `hikari.Role`, `hikari.User`, or `crescent.Mentionable`."
        )

    def get_arg(t: Type[Arg] | Type[Any]) -> Optional[T]:
        data: T
        for data in metadata:
            if isinstance(data, t):
                return getattr(data, "payload", data)
        return None

    name = get_arg(Name) or name
    description = get_arg(Description) or get_arg(str) or "No Description"
    choices = get_arg(Choices)
    channel_types = _channel_types or get_arg(ChannelTypes)
    min_value = get_arg(MinValue)
    max_value = get_arg(MaxValue)

    required = param.default is param.empty

    return CommandOption(
        name=name,
        type=_type,
        description=description,
        choices=choices,
        options=None,
        channel_types=list(channel_types) if channel_types else None,
        min_value=min_value,
        max_value=max_value,
        is_required=required,
    )


def _class_command_callback(
    cls: Type[ClassCommandProto], defaults: Dict[str, Any], name_map: dict[str, str]
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
    callback: CommandCallbackT | Type[ClassCommandProto], /
) -> MetaStruct[CommandCallbackT, AppCommandMeta]:
    ...


@overload
def command(
    *,
    guild: Optional[Snowflakeish] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    deprecated: bool = False,
) -> Callable[
    [CommandCallbackT | Type[ClassCommandProto]], MetaStruct[CommandCallbackT, AppCommandMeta],
]:
    ...


def command(
    callback: CommandCallbackT | Type[ClassCommandProto] | None = None,
    /,
    *,
    guild: Optional[Snowflakeish] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    deprecated: bool = False,
) -> MetaStruct[CommandCallbackT, AppCommandMeta] | Callable[
    [CommandCallbackT | Type[ClassCommandProto]], MetaStruct[CommandCallbackT, AppCommandMeta],
]:
    if not callback:
        return partial(
            command, guild=guild, name=name, description=description, deprecated=deprecated
        )

    if isinstance(callback, type) and isinstance(callback, object):
        defaults: Dict[str, Any] = {}
        options: list[CommandOption] = []
        name_map: dict[str, str] = {}

        for n, v in callback.__dict__.items():
            if not isinstance(v, ClassCommandOption):
                continue
            generated = v._gen_option(n)
            options.append(generated)

            if generated.name != n:
                name_map[generated.name] = n

            defaults[generated.name] = v.default

        callback_func = _class_command_callback(callback, defaults, name_map)

    else:
        callback_func = callback

        options = [
            param
            for param in (_gen_command_option(param) for param in get_parameters(callback_func))
            if param is not None
        ]

    return register_command(
        callback=callback_func,
        command_type=CommandType.SLASH,
        name=name or callback.__name__,
        guild=guild,
        description=description or "No Description",
        options=options,
        deprecated=deprecated,
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
    *, guild: Optional[Snowflakeish] = None, name: Optional[str] = None, deprecated: bool = False
) -> Callable[[UserCommandCallbackT], MetaStruct[UserCommandCallbackT, AppCommandMeta]]:
    ...


def user_command(
    callback: UserCommandCallbackT | None = None,
    /,
    *,
    guild: Optional[Snowflakeish] = None,
    name: Optional[str] = None,
    deprecated: bool = False,
) -> Callable[
    [UserCommandCallbackT], MetaStruct[UserCommandCallbackT, AppCommandMeta]
] | MetaStruct[UserCommandCallbackT, AppCommandMeta]:
    if not callback:
        return partial(user_command, guild=guild, name=name, deprecated=deprecated)

    return register_command(
        callback=_kwargs_to_args_callback(callback),
        command_type=CommandType.USER,
        name=name or callback.__name__,
        guild=guild,
        deprecated=deprecated,
    )


@overload
def message_command(
    callback: MessageCommandCallbackT, /
) -> MetaStruct[MessageCommandCallbackT, AppCommandMeta]:
    ...


@overload
def message_command(
    *, guild: Optional[Snowflakeish] = None, name: Optional[str] = None, deprecated: bool = False
) -> Callable[[MessageCommandCallbackT], MetaStruct[MessageCommandCallbackT, AppCommandMeta]]:
    ...


def message_command(
    callback: MessageCommandCallbackT | None = None,
    /,
    *,
    guild: Optional[Snowflakeish] = None,
    name: Optional[str] = None,
    deprecated: bool = False,
) -> Callable[
    [MessageCommandCallbackT], MetaStruct[MessageCommandCallbackT, AppCommandMeta],
] | MetaStruct[MessageCommandCallbackT, AppCommandMeta]:
    if not callback:
        return partial(message_command, guild=guild, name=name, deprecated=deprecated)

    return register_command(
        callback=_kwargs_to_args_callback(callback),
        command_type=CommandType.MESSAGE,
        name=name or callback.__name__,
        guild=guild,
        deprecated=deprecated,
    )
