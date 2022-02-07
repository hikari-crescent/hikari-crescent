from typing import Sequence

from hikari import _about

from crescent.bot import *
from crescent.commands import *
from crescent.context import *
from crescent.event import *
from crescent.mentionable import *
from crescent.plugin import *
from crescent.typedefs import *

_about.__maintainer__ = "Lunarmagpie"  # type: ignore
_about.__copyright__ = "© 2021 Lunarmagpie"  # type: ignore
_about.__license__ = "MPL 2.0"  # type: ignore

__all__: Sequence[str] = (
    "Description",
    "Name",
    "Choices",
    "ChannelTypes",
    "MaxValue",
    "MinValue",
    "command",
    "user_command",
    "message_command",
    "option",
    "hook",
    "HookResult",
    "Group",
    "SubGroup",
    "Bot",
    "Context",
    "event",
    "CrescentException",
    "AlreadyRegisteredError",
    "CommandNotFoundError",
    "Mentionable",
    "CommandCallbackT",
    "CommandOptionsT",
    "OptionTypesT",
    "HookCallbackT",
    "ClassCommandProto",
    "Plugin",
    "ClassCommandOption",
    "ErrorHandlerCallbackT",
    "catch",
)
