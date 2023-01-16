#  pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false, reportUnknownVariableType=false

# Crescent provides 2 implementations for `crescent.LocaleBuilder`

import hikari

import crescent
from crescent.ext import locales

bot = hikari.GatewayBot(token="...")
client = crescent.Client(bot)

# If you have installed i18n you can use `locales.i18n`
# You must run `pip install hikari-crescent[i18n]` before you can use i18n.

import i18n

i18n.add_translation("name", "english-name", locale="en")
i18n.add_translation("name", "french-name", locale="fr")

i18n.add_translation("description", "english-description", locale="en")
i18n.add_translation("description", "french-description", locale="fr")


# This command will have its name and translation in the french and english locales.
@client.include
@crescent.command(name=locales.i18n("name"), description=locales.i18n("description"))
async def command(ctx: crescent.Context) -> None:
    ...


# There is also `locales.LocaleMap` which allows you to declare translation as kwargs
# when the class is instantiated.
@client.include
@crescent.command(
    name=locales.LocaleMap("name", en_US="english-name", en_GB="english-name", fr="french-name"),
    description=locales.LocaleMap(
        "description",
        en_US="english-description",
        en_GB="english-description",
        fr="french-description",
    ),
)
async def command_2(ctx: crescent.Context) -> None:
    ...


bot.run()
