from typing import Sequence

__all__: Sequence[str] = ("CrescentException", "AlreadyRegisteredError", "CommandNotFoundError")


class CrescentException(Exception):
    """Base Exception for all exceptions Crescent throws"""


class AlreadyRegisteredError(CrescentException):
    """Command or exception catch function was already registered"""


class CommandNotFoundError(CrescentException):
    """Command was not registered locally"""
