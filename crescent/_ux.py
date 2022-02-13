from contextlib import redirect_stdout
from io import StringIO
from string import Template
from sys import stdout
from typing import Dict, Sequence

from hikari.internal.ux import print_banner as _print_banner

from crescent._about import __copyright__, __license__

__all__: Sequence[str] = ("print_banner",)


def print_banner(banner: str, allow_color: bool, force_color: bool):
    # Prevent circular import
    from crescent import __version__

    buffer = StringIO()

    with redirect_stdout(buffer):
        _print_banner(banner, allow_color, force_color)

    args: Dict[str, str] = {
        "crescent_version": __version__,
        "crescent_copyright": __copyright__,
        "crescent_license": __license__,
    }

    stdout.write(Template(buffer.getvalue()).safe_substitute(args))
