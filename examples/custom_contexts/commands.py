import typing

import hikari

import crescent

bot = hikari.GatewayBot(token="...")
client = crescent.Client(bot)


# All custom contexts must inherit from `crescent.BaseContext` or a subclass, such
# as `crescent.Context`.
# `BaseContext` does not define any methods. It only stores data from the interaction.
class CustomContext(crescent.BaseContext):
    def a_custom_method(self) -> str:
        return "Hello there"


class CustomContext2(crescent.Context):
    ...


@client.include
@crescent.command
# To use a custom context, simply use the context object you want as the type hint.
async def my_command(ctx: CustomContext) -> None:
    # The custom method can now be called.
    message = ctx.a_custom_method()

    # The type of a context can changed with the `BaseContext.into` method.
    crescent_ctx: crescent.Context = ctx.into(crescent.Context)

    # Methods on `crescent.Context` can now be used.
    await crescent_ctx.respond(message)


# A custom context type can be provided to command error handlers
@client.include
@crescent.catch_command(Exception)
async def error_handle(exc: Exception, ctx: CustomContext) -> None:
    ...


# Autocomplete callbacks also support custom contexts.
async def autocomplete_callback(
    ctx: CustomContext, option: hikari.AutocompleteInteractionOption
) -> typing.List[typing.Tuple[str, str]]:
    return []


# Autocomplete error handlers also support custom contexts.
@client.include
@crescent.catch_autocomplete(Exception)
async def autocomplete_error_handler(
    exc: Exception, ctx: CustomContext, option: hikari.AutocompleteInteractionOption
) -> None:
    ...


@client.include
@crescent.command(name="has_autocomplete")
class HasAutocomplete:
    option = crescent.option(str, autocomplete=autocomplete_callback)

    async def callback(self, ctx: CustomContext) -> None:
        ...


bot.run()
