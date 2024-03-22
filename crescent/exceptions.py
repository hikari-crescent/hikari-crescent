from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from crescent.typedefs import ClassCommandProto

__all__: Sequence[str] = (
    "CrescentException",
    "ConverterExceptions",
    "ConverterExceptionMeta",
    "AlreadyRegisteredError",
    "PluginAlreadyLoadedError",
    "PermissionsError",
)


class CrescentException(Exception):
    """Base Exception for all exceptions Crescent throws"""


@dataclass
class ConverterExceptionMeta:
    command: type[ClassCommandProto]
    option_key: str
    """The key of the option on the command class"""
    value: Any
    """The unconverted value"""
    exception: Exception


class ConverterExceptions(CrescentException):
    """One or more errors occurred while running the converters for a command."""

    def __init__(self, errors: list[ConverterExceptionMeta]) -> None:
        self.errors = errors
        args: list[Any] = []
        for e in errors:
            args.extend(e.exception.args)
        super().__init__(*args)


class AlreadyRegisteredError(CrescentException):
    """Command or exception catch function was already registered"""


class PluginAlreadyLoadedError(CrescentException):
    """A plugin is attempted to be loaded but the plugin manager already loaded the plugin."""


class PermissionsError(CrescentException):
    """Raise when a permission is declared in a subcommand"""


class InteractionAlreadyAcknowledgedError(CrescentException):
    """Raise when an interaction is already acknowledged"""
