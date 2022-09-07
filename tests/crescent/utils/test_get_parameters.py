from __future__ import annotations

from crescent.utils import get_parameters


def test_postponed_evaluation():
    """
    Ensures that lowercase `list`, `dict`, `tuple`, and `type` work in python <3.10 for
    functions passed into `get_parameters`.
    """

    def function(a: list[str], b: dict[str, str], c: tuple[str], d: type[str]):
        ...

    get_parameters(function)
