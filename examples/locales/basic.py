# Locales can be used by subclassing `crescent.LocaleBuilder`
# NOTE: `crescent.ext.locales` provides implementations of `crescent.LocaleBuilder` that
# may work for your usecase.

from __future__ import annotations

import crescent
import dataclasses


bot = crescent.Bot("...")


@dataclasses.dataclass
class Locale(crescent.LocaleBuilder):

    _fallback: str
    en_US: str

    # Build must return a subclass of `typing.Mapping`.
    def build(self) -> dict[str, str]:
        """Return a dict of command localization names to values."""

        # All possible locales can be seen in the `hikari.Locale` enum.
        return {"en-US": self.en_US}

    @property
    def fallback(self) -> str:
        return self._fallback


# This command's name is "en-name" for users on the `en-US` locale. Otherwise the
# command will be displayed as "name". The same pattern follows for the description.
@bot.include
@crescent.command(
    name=Locale("name", en_US="en-name"), description=Locale("description", en_US="en-description")
)
class Command:
    # "en-option-name" and "en-option-description" will be used when the user is
    # using the `en-US` locale. Otherwise "option-name" and "option-description"
    # will be visible.
    word = crescent.option(
        str,
        name=Locale("option-name", en_US="en-option-name"),
        description=Locale("option-description", en_US="en-option-description"),
    )

    async def callback(self, ctx: crescent.Context) -> None:
        # The locale of the user who ran the command can be viewed with `Context.locale`
        await ctx.respond(ctx.locale)


bot.run()
