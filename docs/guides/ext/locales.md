# Locales

Locales are used to localize your bot for different regions and languages.

## Locale Map

Locale map is a simple way to use locales is [`LocaleMap`][locales.LocaleMap].


```python
import hikari
import crescent
from crescent.ext import locales

bot = hikari.GatewayBot(token="YOUR_TOKEN")
client = crescent.Client(bot)

locale_map = locales.LocaleMap("name", en_US="english-name", en_GB="english-name", fr="french-name")

@client.include
@crescent.command(
    name=locale_map,
    description=locales.LocaleMap(
        "description",
        en_US="english-description",
        en_GB="english-description",
        fr="french-description",
    ),
)
async def command_2(ctx: crescent.Context) -> None:
    ...
```

The `i18n` library can also be used for locales with the [`i18n`][locales.i18n] object. You should check
the `i18n` documentation for more information.

!!! warning

    You must install the `i18n` library with `hikari-crescent[i18n]` to
    use `i18n`.


```python
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
```
