from typing import Sequence

__all__: Sequence[str] = (
    "CrescentException",
    "AlreadyRegisteredError",
    "PluginAlreadyLoadedError",
)


class CrescentException(Exception):
    """Base Exception for all exceptions Crescent throws"""


class AlreadyRegisteredError(CrescentException):
    """Command or exception catch function was already registered"""


class PluginAlreadyLoadedError(CrescentException):
    """A plugin is attempted to be loaded but the plugin manager already loaded the plugin."""
