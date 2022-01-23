from __future__ import annotations

from functools import partial
from inspect import Parameter, signature
from typing import TYPE_CHECKING

from hikari import (
    CommandOption,
    OptionType,
    PartialChannel,
    Role,
    Snowflake,
    User,
)

from crescent.commands.args import (
    Arg,
    ChannelTypes,
    Choices,
    MaxValue,
    MinValue,
    Name,
    Description,
)
from crescent.context import Context
from crescent.internal.registry import register_command
from crescent.mentionable import Mentionable

if TYPE_CHECKING:
    from typing import Any, Optional, Type, Dict, Sequence, TypeVar

    T = TypeVar("T")

__all__: Sequence[str] = (
    "command",
)

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


def _gen_command_option(param: Parameter) -> Optional[CommandOption]:
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
        is_required=required
    )


def command(
    callback=None,
    guild: Optional[Snowflake] = None,
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
            description=description
        )

    options: Sequence[CommandOption] = tuple(
        param for param in
        (
            _gen_command_option(param)
            for param in signature(callback).parameters.values()
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
        options=options
    )
