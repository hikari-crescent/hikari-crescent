from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Tuple, Type, Union, get_args, get_origin

from hikari import CommandOption, OptionType

from crescent.commands.args import (
    Arg,
    Autocomplete,
    ChannelTypes,
    Choices,
    Description,
    MaxValue,
    MinValue,
    Name,
)
from crescent.commands.options import OPTIONS_TYPE_MAP, get_channel_types
from crescent.context import Context

if TYPE_CHECKING:
    from inspect import Parameter
    from typing import Any, Optional, Sequence, TypeVar

    from crescent.typedefs import AutocompleteCallbackT

    T = TypeVar("T")

__all__: Sequence[str] = ("gen_command_option", "get_autocomplete_func")

NoneType = type(None)


def _unwrap_optional(origin: Type[Any]) -> Any:
    if get_origin(origin) is not Union:
        return origin

    args = get_args(origin)

    if len(args) != 2 or NoneType not in args:
        return args

    if args[1] is NoneType:
        return args[0]

    return args[1]


def _get_arg(t: Type[Arg] | Type[Any], metadata: Iterable[Any]) -> Optional[T]:
    data: T
    for data in metadata:
        if isinstance(data, t):
            return getattr(data, "payload", data)
    return None


def _get_origin_and_metadata(param: Parameter) -> Tuple[Any, Iterable[Any]]:
    typehint = param.annotation
    origin = _unwrap_optional(typehint)
    metadata = ()

    if hasattr(origin, "__metadata__"):
        metadata = origin.__metadata__
        origin = _unwrap_optional(origin.__origin__)

    return origin, metadata


def gen_command_option(param: Parameter) -> Optional[CommandOption]:
    name = param.name

    origin, metadata = _get_origin_and_metadata(param)

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

    name = _get_arg(Name, metadata) or name
    description = _get_arg(Description, metadata) or _get_arg(str, metadata) or "No Description"
    choices = _get_arg(Choices, metadata)
    channel_types = _channel_types or _get_arg(ChannelTypes, metadata)
    min_value = _get_arg(MinValue, metadata)
    max_value = _get_arg(MaxValue, metadata)
    autocomplete = _get_arg(Autocomplete, metadata)

    required = param.default is param.empty

    return CommandOption(
        name=name,
        autocomplete=bool(autocomplete),
        type=_type,
        description=description,
        choices=choices,
        options=None,
        channel_types=list(channel_types) if channel_types else None,
        min_value=min_value,
        max_value=max_value,
        is_required=required,
    )


def get_autocomplete_func(param: Parameter) -> Optional[AutocompleteCallbackT]:
    _, metadata = _get_origin_and_metadata(param)
    return _get_arg(Autocomplete, metadata)
