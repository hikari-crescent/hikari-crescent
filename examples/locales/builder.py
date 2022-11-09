# Locales can be used by subclassing `crescent.LocaleBuilder`

import crescent
import dataclasses
import typing


bot = crescent.Bot("...")


@dataclasses.dataclass
class Locale(crescent.LocaleBuilder):

    default_name: str
    en_US: str

    def build(self) -> typing.MutableMapping[str, str]:
        """Return a dict of command localization names to values."""

        return {"en-US": "english-name"}

    def default(self) -> str:
        "This value is used as the default."
        return self.default_name


# This command's name is "en-name" for users on the `en-US` locale. Otherwise the
# command will be displayed as "name". The same pattern follows for the description.
@bot.include
@crescent.command(
    name=Locale("name", en_US="en-name"), description=Locale("description", en_US="en-description")
)
class command:
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
