from typing import Sequence

__all__: Sequence[str] = ("CrescentException", "CommandNotFoundError")


class CrescentException(Exception):
    """Base Exception for all exceptions Crescent throws"""


class CommandNotFoundError(CrescentException):
    """Command was not registered locally"""
