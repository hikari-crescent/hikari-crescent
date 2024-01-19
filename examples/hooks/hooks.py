import hikari

import crescent

# Hooks allow you to execute functions before or after command
# They execute in this order: command -> subgroup -> group -> plugin -> client


async def first_hook(ctx: crescent.Context) -> crescent.HookResult:  # you can also return None
    print("Here first.")
    # Setting exit to true prevents any following hooks and the callback from
    # being run.
    await ctx.respond("INTERCEPTED")
    return crescent.HookResult(exit=True)


def second_hook(number: int) -> crescent.CommandHookCallbackT:
    async def inner(ctx: crescent.Context) -> None:
        print(f"Here second. Number is {number}")
        ctx.options["number"] = number

    return inner


bot = hikari.GatewayBot(token="...")
client = crescent.Client(bot)


@client.include
@crescent.hook(first_hook, second_hook(5))
@crescent.command(name="test-command")
class TestCommand:
    number = crescent.option(int)

    async def callback(self, ctx: crescent.Context) -> None:
        # This code will never be reached due to `first_hook`
        await ctx.respond("Done!")


# This code is equlivent to equivalent to the previous function.
@client.include
@crescent.hook(first_hook)
@crescent.hook(second_hook(5))
@crescent.command(name="test-command-two")
class TestCommand2:
    number = crescent.option(int)

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.respond("Done!")


bot.run()
