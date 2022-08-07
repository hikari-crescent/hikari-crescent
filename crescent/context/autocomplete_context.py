from typing import Sequence

from hikari import CommandInteraction

from crescent.context.base_context import BaseContext

__all__: Sequence[str] = ("AutocompleteContext",)


class AutocompleteContext(BaseContext):
    """Represents the context for autocomplete interactions"""

    interaction: CommandInteraction
