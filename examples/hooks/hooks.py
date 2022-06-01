import crescent


async def first_hook(ctx: crescent.Context) -> crescent.HookResult:  # you can also return None
    print("Here first.")
    # Setting exit to true prevents any following hooks and the callback from
    # being run.
    await ctx.respond("INTERCEPTED")
    return crescent.HookResult(exit=True)


def second_hook(number: int) -> crescent.HookCallbackT:
    async def inner(ctx: crescent.Context) -> None:
        print(f"Here second. Number is {number}")
        ctx.options["numeber"] = number

    return inner


bot = crescent.Bot(token="...")


@bot.include
@crescent.hook(first_hook)
@crescent.hook(second_hook(5))
@crescent.command
async def test_command(ctx: crescent.Context, number: int):
    # This code will never be reached due to `first_hook`
    await ctx.respond("Done!")


bot.run()
