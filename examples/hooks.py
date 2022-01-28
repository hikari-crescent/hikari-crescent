import crescent


async def first_hook(ctx: crescent.Context):
    print("Here first.")
    # Setting exit to true prevents any following hooks and the callback from
    # being run.
    await ctx.respond("INTERCEPTED")
    return crescent.HookResult(exit=True)


def second_hook(number: int):
    async def inner(ctx: crescent.Context):
        print(f"Here second. Number is {number}")
    return inner


bot = crescent.Bot(token="...")


@crescent.hook(first_hook)
@crescent.hook(second_hook(5))
@bot.include
@crescent.command
async def test_command(ctx: crescent.Context):
    # This code will never be reached due to `second_hook`
    await ctx.respond("Done!")

bot.run()
