import crescent

# Groups can also have hooks. Hooks will resolved in the order of decorators.
# When using a `crescent.SubGroup` the group's hooks will be executed before the
# sub group's hooks.

bot = crescent.Bot(token="...")


async def first_hook(ctx: crescent.Context):
    print("Here first.")


async def second_hook(ctx: crescent.Context):
    print("Here second.")


async def third_hook(ctx: crescent.Context):
    print("Here third.")


group = crescent.Group("my_group", hooks=[first_hook], after_hooks=[first_hook])
sub_group = group.sub_group("my_sub_group", hooks=[second_hook], after_hooks=[second_hook])


# Hooks execute in order before the command:
# second_hook
# first_hook
# third_hook

# Hooks execute in order after the command:
# second_hook
# first_hook
# third_hook


@bot.include
@sub_group.child
@crescent.hook(third_hook)
@crescent.hook(third_hook, after=True)
@crescent.command
async def say(ctx: crescent.Context, word: str):
    await ctx.respond(word)


bot.run()
