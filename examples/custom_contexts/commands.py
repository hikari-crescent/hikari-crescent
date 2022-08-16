import typing

import hikari
import crescent

bot = crescent.Bot("...")

# All custom contexts must inherit from `BaseContext``
# `BaseContext` does not define any methods. It only stores data from the interaction.
class CustomContext(crescent.BaseContext):
    def a_custom_method(self) -> str:
        return "Hello there"


@bot.include
@crescent.command
# To use a custom context, simply use the context object you want as the type hint.
async def my_command(ctx: CustomContext) -> None:
    # The custom method can now be called
    message = ctx.a_custom_method()

    # The type of a context can changed with the `BaseContext.into` function
    crescent_ctx: crescent.Context = ctx.into(crescent.Context)

    # Methods on `crescent.Context` can now be used.
    await crescent_ctx.respond(message)


# A custom context type can be provided to command error handlers
@bot.include
@crescent.catch_command(Exception)
async def error_handle(exc: Exception, ctx: CustomContext) -> None:
    ...


# Autocomplete callbacks also support custom contexts.
async def autocomplete_callback(
    ctx: CustomContext, option: hikari.AutocompleteInteractionOption
) -> typing.List[hikari.CommandChoice]:
    return []


@bot.include
@crescent.command(name="has_autocomplete")
class HasAutocomplete:
    option = crescent.option(str, autocomplete=autocomplete_callback)

    async def callback(self, ctx: CustomContext) -> None:
        ...


bot.run()
