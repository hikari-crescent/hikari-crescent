from typing import Dict, Optional, Sequence

from hikari.internal.ux import print_banner as _print_banner

from crescent._about import __copyright__, __license__

__all__: Sequence[str] = ("print_banner",)


def print_banner(banner: Optional[str], allow_color: bool, force_color: bool):
    # Prevent circular import
    from crescent import __version__

    args: Dict[str, str] = {
        "crescent_version": __version__,
        "crescent_copyright": __copyright__,
        "crescent_license": __license__,
    }

    _print_banner(banner, allow_color, force_color, extra_args=args)
