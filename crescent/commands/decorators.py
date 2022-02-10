from __future__ import annotations

from functools import partial
from inspect import signature
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    Dict,
    NamedTuple,
    Type,
    Union,
    get_args,
    get_origin,
    get_type_hints,
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

if TYPE_CHECKING:
    from inspect import Parameter, _empty
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


class _Parameter(NamedTuple):
    name: str
    annotation: Type[Any]
    empty: Type[_empty]
    default: Any


def _gen_command_option(param: _Parameter) -> Optional[CommandOption]:
    name = param.name
    typehint = param.annotation

    metadata = ()

    origin = typehint
    if hasattr(typehint, "__metadata__"):
        metadata = typehint.__metadata__
        origin = typehint.__origin__

    if origin is Context or origin is param.empty:
        return None

    # Support for `Optional` typehint
    if get_origin(origin) is Union:
        args = get_args(origin)
        if len(args) == 2 and NoneType in args:
            origin = args[0] if args[1] is NoneType else args[1]
        else:
            raise ValueError("Typehint must be `T`, `Optional[T]`, or `Union[T, None]`")

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
            if type(data) == t:
                return getattr(data, "payload", data)
        return None

    name = get_arg(Name) or name
    description = get_arg(Description) or get_arg(str) or "\u200B"
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
    async def callback(*args, **kwargs) -> Any:
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
):
    if not callback:
        return partial(command, guild=guild, name=name, description=description)

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

        # NOTE: If python 3.10 becomes the minimum supported version, this section
        # can be replaced with `signature(callback, eval_str=True)`

        type_hints = get_type_hints(callback)

        def convert_signiture(param: Parameter) -> _Parameter:
            annotation = type_hints.get(param.name, None)
            return _Parameter(
                name=param.name,
                annotation=annotation or param.annotation,
                empty=param.empty,
                default=param.default,
            )

        sig = map(convert_signiture, signature(callback_func).parameters.values())

        options = [
            param for param in (_gen_command_option(param) for param in sig) if param is not None
        ]

    return register_command(
        callback=callback_func,
        command_type=CommandType.SLASH,
        name=name or callback.__name__,
        guild=guild,
        description=description or "\u200b",
        options=options,
    )


def _kwargs_to_args_callback(callback: Callable[..., Awaitable[Any]]):
    async def inner(ctx: Context, **kwargs):
        return await callback(ctx, *kwargs.values())

    return inner


def user_command(
    callback: UserCommandCallbackT | None = None,
    /,
    *,
    guild: Optional[Snowflakeish] = None,
    name: Optional[str] = None,
):
    if not callback:
        return partial(user_command, guild=guild, name=name)

    return register_command(
        callback=_kwargs_to_args_callback(callback),
        command_type=CommandType.USER,
        name=name or callback.__name__,
        guild=guild,
    )


def message_command(
    callback: MessageCommandCallbackT | None = None,
    /,
    *,
    guild: Optional[Snowflakeish] = None,
    name: Optional[str] = None,
):
    if not callback:
        return partial(message_command, guild=guild, name=name)

    return register_command(
        callback=_kwargs_to_args_callback(callback),
        command_type=CommandType.MESSAGE,
        name=name or callback.__name__,
        guild=guild,
    )
