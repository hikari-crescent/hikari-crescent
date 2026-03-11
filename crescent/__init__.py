from __future__ import annotations

from importlib.metadata import version

from crescent.client import Client, GatewayTraits, RESTTraits
from crescent.commands import Group, SubGroup, command, message_command, options, user_command
from crescent.context import AutocompleteContext, Context
from crescent.errors import catch_autocomplete, catch_command, catch_event
from crescent.events import event
from crescent.exceptions import (
    AlreadyRegisteredError,
    ConverterExceptionMeta,
    ConverterExceptions,
    CrescentException,
    PermissionsError,
    PluginAlreadyLoadedError,
)
from crescent.hooks import HookResult, hook
from crescent.locale import LocaleBuilder
from crescent.mentionable import Mentionable
from crescent.plugin import Plugin, PluginManager
from crescent.typedefs import (
    AutocompleteCallbackT,
    ClassCommandProto,
    CommandCallbackT,
    CommandHookCallbackT,
    CommandOptionsT,
    OptionTypesT,
)

__version__: str = version("hikari-crescent")

__all__ = (
    "AlreadyRegisteredError",
    "AutocompleteCallbackT",
    "AutocompleteContext",
    "ClassCommandProto",
    "Client",
    "CommandCallbackT",
    "CommandHookCallbackT",
    "CommandOptionsT",
    "Context",
    "ConverterExceptionMeta",
    "ConverterExceptions",
    "CrescentException",
    "GatewayTraits",
    "Group",
    "HookResult",
    "LocaleBuilder",
    "Mentionable",
    "OptionTypesT",
    "PermissionsError",
    "Plugin",
    "PluginAlreadyLoadedError",
    "PluginManager",
    "RESTTraits",
    "SubGroup",
    "catch_autocomplete",
    "catch_command",
    "catch_event",
    "command",
    "event",
    "hook",
    "message_command",
    "options",
    "user_command",
)
