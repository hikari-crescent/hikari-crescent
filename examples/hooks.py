import crescent


@crescent.interaction_hook
async def first_hook(ctx: crescent.Context):
    print("here first")


@crescent.interaction_hook
async def second_hook(ctx: crescent.Context):
    print("here second")
    # Setting exit to true prevents any following hooks and the callback from
    # being run.
    await ctx.respond("INTERCEPTED")
    return crescent.HookResult(exit=True)


bot = crescent.Bot(token="...")


@first_hook
@second_hook
@bot.include
@crescent.command
async def test_command(ctx: crescent.Context):
    # This code will never be reached due to `second_hook`
    await ctx.respond("Done!")
