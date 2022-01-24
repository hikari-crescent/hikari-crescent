from __future__ import annotations

from collections import namedtuple
from functools import partial
from inspect import Parameter, signature
from typing import TYPE_CHECKING, get_type_hints

from hikari import CommandOption, OptionType, PartialChannel, Role, Snowflakeish, User

from crescent.commands.args import (
    Arg,
    ChannelTypes,
    Choices,
    Description,
    MaxValue,
    MinValue,
    Name,
)
from crescent.context import Context
from crescent.internal.registry import register_command
from crescent.mentionable import Mentionable

if TYPE_CHECKING:
    from typing import Any, Dict, Optional, Sequence, Type, TypeVar

    T = TypeVar("T")

__all__: Sequence[str] = ("command",)

_OPTIONS_TYPE_MAP: Dict[Type, OptionType] = {
    str: OptionType.STRING,
    bool: OptionType.BOOLEAN,
    int: OptionType.INTEGER,
    float: OptionType.FLOAT,
    PartialChannel: OptionType.CHANNEL,
    Role: OptionType.ROLE,
    User: OptionType.USER,
    Mentionable: OptionType.MENTIONABLE,
}

_Parameter = namedtuple(
    "_Parameter",
    ("name", "annotation", "empty", "default")
)


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

    _type = _OPTIONS_TYPE_MAP[origin]

    def get_arg(t: Type[Arg] | Type[Any]) -> Optional[T]:
        data: T
        for data in metadata:
            if type(data) == t:
                return getattr(data, "payload", data)
        return None

    name = get_arg(Name) or name
    description = get_arg(Description) or get_arg(str) or "\u200B"
    choices = get_arg(Choices)
    channel_types = get_arg(ChannelTypes)
    min_value = get_arg(MinValue)
    max_value = get_arg(MaxValue)

    required = param.default is param.empty

    return CommandOption(
        name=name,
        type=_type,
        description=description,
        choices=choices,
        options=None,
        channel_types=channel_types,
        min_value=min_value,
        max_value=max_value,
        is_required=required,
    )


def command(
    callback=None,
    guild: Optional[Snowflakeish] = None,
    name: Optional[str] = None,
    group: Optional[str] = None,
    sub_group: Optional[str] = None,
    description: Optional[str] = None,
):
    if not callback:
        return partial(
            command,
            name=name,
            group=group,
            sub_group=sub_group,
            description=description,
        )

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

    sig = map(convert_signiture, signature(callback).parameters.values())

    options: Sequence[CommandOption] = tuple(
        param
        for param in (
            _gen_command_option(param)
            for param in sig
        )
        if param is not None
    )

    return register_command(
        callback=callback,
        guild=guild,
        name=name,
        group=group,
        sub_group=sub_group,
        description=description,
        options=options,
    )
