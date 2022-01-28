from typing import Optional
import crescent
from crescent.commands.hooks import HookResult
from crescent.typedefs import CommandOptionsT, HookCallbackT


async def first_hook(ctx: crescent.Context, options: CommandOptionsT) -> Optional[HookResult]:
    print("Here first.")
    # Setting exit to true prevents any following hooks and the callback from
    # being run.
    await ctx.respond("INTERCEPTED")
    return crescent.HookResult(exit=True)


def second_hook(number: int) -> HookCallbackT:
    async def inner(ctx: crescent.Context, options: CommandOptionsT) -> Optional[HookResult]:
        print(f"Here second. Number is {number}")
        options["number"] = number
        return HookResult(options=options)
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
