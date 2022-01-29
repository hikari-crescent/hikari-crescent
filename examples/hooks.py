from typing import Optional

import crescent


async def first_hook(
    ctx: crescent.Context,
    # options is a shallow copy of the options from the interaction
    options: crescent.CommandOptionsT,
) -> Optional[crescent.HookResult]:
    print("Here first.")
    # Setting exit to true prevents any following hooks and the callback from
    # being run.
    await ctx.respond("INTERCEPTED")
    return crescent.HookResult(exit=True)


def second_hook(number: int) -> crescent.HookCallbackT:
    async def inner(
        ctx: crescent.Context, options: crescent.CommandOptionsT
    ) -> Optional[crescent.HookResult]:
        print(f"Here second. Number is {number}")
        options["number"] = number
        return crescent.HookResult(options=options)

    return inner


bot = crescent.Bot(token="...")


@crescent.hook(first_hook)
@crescent.hook(second_hook(5))
@bot.include
@crescent.command
async def test_command(ctx: crescent.Context, number: int):
    # This code will never be reached due to `second_hook`
    await ctx.respond("Done!")


bot.run()
