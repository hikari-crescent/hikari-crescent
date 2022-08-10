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
