from importlib.metadata import version
from typing import Sequence

from crescent.client import *
from crescent.commands import *
from crescent.context import *
from crescent.errors import *
from crescent.event import *
from crescent.exceptions import *
from crescent.locale import *
from crescent.mentionable import *
from crescent.plugin import *
from crescent.typedefs import *

__version__: str = version("hikari-crescent")

__all__: Sequence[str] = (
    "Description",
    "Name",
    "Choices",
    "ChannelTypes",
    "MaxValue",
    "MinValue",
    "Autocomplete",
    "command",
    "user_command",
    "message_command",
    "option",
    "hook",
    "HookResult",
    "Group",
    "SubGroup",
    "Client",
    "GatewayTraits",
    "RESTTraits",
    "Context",
    "AutocompleteContext",
    "catch_command",
    "catch_event",
    "catch_autocomplete",
    "event",
    "CrescentException",
    "AlreadyRegisteredError",
    "PluginAlreadyLoadedError",
    "PermissionsError",
    "LocaleBuilder",
    "Mentionable",
    "CommandCallbackT",
    "CommandOptionsT",
    "OptionTypesT",
    "HookCallbackT",
    "AutocompleteCallbackT",
    "ClassCommandProto",
    "Plugin",
    "PluginManager",
    "ClassCommandOption",
)
