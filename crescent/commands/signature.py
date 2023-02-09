from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Iterable, Union, get_args, get_origin

from hikari import CommandOption, OptionType

from crescent.commands.args import (
    Arg,
    Autocomplete,
    ChannelTypes,
    Choices,
    Description,
    MaxLength,
    MaxValue,
    MinLength,
    MinValue,
    Name,
)
from crescent.commands.options import OPTIONS_TYPE_MAP, get_channel_types
from crescent.context import BaseContext
from crescent.locale import LocaleBuilder, str_or_build_locale
from crescent.utils import any_issubclass

if TYPE_CHECKING:
    from typing import Any, Sequence, TypeVar

    from sigparse import Parameter

    from crescent.typedefs import AutocompleteCallbackT

    T = TypeVar("T")

_LOG = getLogger(__name__)

__all__: Sequence[str] = ("gen_command_option", "get_autocomplete_func")

NoneType: type[None] = type(None)


def _unwrap_optional(origin: type[Any]) -> Any:
    args = get_args(origin)

    if len(args) == 2 and NoneType in args:
        return next(filter(lambda x: x is not NoneType, args))

    if get_origin(origin) is not Union:
        return origin

    return args


def _get_arg(t: type[Arg] | type[Any], metadata: Iterable[Any]) -> Any | None:
    for data in metadata:
        if isinstance(data, t):
            return getattr(data, "payload", data)
    return None


def _get_origin_and_metadata(param: Parameter) -> tuple[Any, Iterable[Any]]:
    typehint = param.annotation
    origin = _unwrap_optional(typehint)
    metadata = ()

    if hasattr(origin, "__metadata__"):
        metadata = origin.__metadata__
        origin = _unwrap_optional(origin.__origin__)

    return origin, metadata


def gen_command_option(param: Parameter) -> CommandOption | None:
    if not param.has_annotation:
        return None

    origin, metadata = _get_origin_and_metadata(param)

    if any_issubclass(origin, BaseContext):
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

    name = _get_arg(Name, metadata) or param.name
    description = (
        _get_arg(Description, metadata)
        or _get_arg(str, metadata)
        or _get_arg(LocaleBuilder, metadata)
        or "No Description"
    )

    name, name_localizations = str_or_build_locale(name)
    description, description_localizations = str_or_build_locale(description)

    choices = _get_arg(Choices, metadata)
    channel_types = _channel_types or _get_arg(ChannelTypes, metadata)
    min_value = _get_arg(MinValue, metadata)
    max_value = _get_arg(MaxValue, metadata)
    min_length = _get_arg(MinLength, metadata)
    max_length = _get_arg(MaxLength, metadata)
    autocomplete = _get_arg(Autocomplete, metadata)

    required = not param.has_default

    return CommandOption(
        name=name,
        name_localizations=name_localizations,
        autocomplete=bool(autocomplete),
        type=_type,
        description=description,
        description_localizations=description_localizations,
        choices=choices,
        options=None,
        channel_types=list(channel_types) if channel_types else None,
        min_value=min_value,
        max_value=max_value,
        min_length=min_length,
        max_length=max_length,
        is_required=required,
    )


def get_autocomplete_func(param: Parameter) -> AutocompleteCallbackT | None:
    _, metadata = _get_origin_and_metadata(param)
    return _get_arg(Autocomplete, metadata)
