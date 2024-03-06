from __future__ import annotations

from typing import Any, Sequence

__all__: Sequence[str] = (
    "CrescentException",
    "ConverterException",
    "AlreadyRegisteredError",
    "PluginAlreadyLoadedError",
    "PermissionsError",
)


class CrescentException(Exception):
    """Base Exception for all exceptions Crescent throws"""


class ConverterException(CrescentException):
    """One or more errors occurred while running the converters for a command."""

    def __init__(self, errors: list[Exception]) -> None:
        self.errors = errors
        args: list[Any] = []
        for e in errors:
            args.extend(e.args)
        super().__init__(*args)


class AlreadyRegisteredError(CrescentException):
    """Command or exception catch function was already registered"""


class PluginAlreadyLoadedError(CrescentException):
    """A plugin is attempted to be loaded but the plugin manager already loaded the plugin."""


class PermissionsError(CrescentException):
    """Raise when a permission is declared in a subcommand"""


class InteractionAlreadyAcknowledgedError(CrescentException):
    """Raise when an interaction is already acknowledged"""
