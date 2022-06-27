import crescent

# Plugins can be added to plugins or the bot. Adding commands to the bot works
# exactly the same as plugins.


async def first_hook(ctx: crescent.Context) -> None:
    pass


async def second_hook(ctx: crescent.Context) -> None:
    pass


plugin = crescent.Plugin(
    "example",
    command_hooks=[first_hook],  # Hooks to execute before the command
    command_after_hooks=[first_hook],  # Hooks to execute after the command
)

# Hooks execute in this order:
# first_hook
# second_hook

# After the command first hook will execute


@plugin.include
@crescent.hook(second_hook)
@crescent.command
async def say(ctx: crescent.Context, word: str) -> None:
    await ctx.respond(word)
