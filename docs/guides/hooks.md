# Hooks

Hooks allow you to run code before or after a command is run or an event is processed. They also allow you
to create checks for a certain command.

This is a simple command hook that says "hello there" before every command you hook it to.

```python
async def my_hook(ctx: crescent.Context) -> None:
    await ctx.respond("Hello there")
```

To use this hook on a command, simply do:
```python

@client.include
@crescent.hook(my_hook)
@crescent.command
async def my_command(ctx: crescent.Context) -> None:
    await ctx.respond("General Kenobi")
```

This command will respond "Hello there" and "General kenobi" in two different messages.


You can access command options in hooks with `ctx.options`. This is a dict of option name to
option value.


## Using hooks as checks

You can also stop a command callback from running in a hook. Simply return `crescent.HookResult(exit=True)`

This is a command that uses that feature. It stops you from using the command if your name has an "L" in it.

```python
async def no_Ls_allowed(ctx: crescent.Context) -> crescent.HookResult:
    if "l" in ctx.user.username.lower():
        await ctx.respond("You can't use this command!")
        return crescent.HookResult(exit=True)

    return crescent.HookResult()

@client.include
@crescent.hook(no_Ls_allowed)
@crescent.command
async def my_command(ctx: crescent.Context) -> None:
    await ctx.respond("Hello")
```

## Running a hook after a command
To run a hook after a command, add `after=True` to the decorator.
This command will return "General Kenobi" then "Hello there" in two separate messages.
```python
async def my_hook(ctx: crescent.Context) -> None:
    await ctx.respond("Hello there")
```

To use this hook on a command, simply do:
```python
@client.include
@crescent.hook(my_hook, after=True)
@crescent.command
async def my_command(ctx: crescent.Context) -> None:
    await ctx.respond("General Kenobi")
```

## Adding hooks to more than commands

Bots and plugins (we will cover these later) support hooks by adding them with the
`command_hooks` and `command_after_hooks` kwargs. Hooks on the bot object will run
for all commands. Hooks on the plugin object will run for all commands in that plugin.

```python
bot = crescent.Bot("...", command_hooks=[hook_a, hook_b])
```

`crescent.Group` and `crescent.SubGroup` also support hooks. Use the `hooks` and `after_hooks`
kwargs to add them. Groups and sub groups will add hooks to any commands in their respective
groups.

```python
group = crescent.Group("group", hooks=[hook_a])
sub_group = group.sub_group("sub-group", hooks=[hook_b])
```

Sub groups will inherit all hooks from the group.

### Hook Resolution Order
`Command -> Sub Group -> Group -> Plugin -> Bot`

## Using hooks for ratelimiting

One of crescent's built in extensions is `crescent.ext.cooldowns`, allowing for rate limiting.
To use this extension, you must install `hikari-crescent[cooldowns]`.

```python
import crescent
import datetime
from crescent.ext import cooldowns

bucket_size = 1
delay = datetime.timedelta(seconds=20)

@client.include
@crescent.hook(cooldowns.cooldown(bucket_size, delay))
@crescent.command
async def my_command(ctx: crescent.Context) -> None:
    await ctx.respond("General Kenobi")
```

To see more information on this function, check the API reference for `crescent.ext.cooldowns`.


## Event Hooks

Hooks can be used for events. An event callback can use any hook for the event type
or supertype of the event type in the callback.

```python
async def human_only(event: hikari.MessageCreateEvent) -> crescent.HookResult:
    if not event.is_human:
        return crescent.HookResult(exit=True)
    return crescent.HookResult()


@client.include
@crescent.hook(human_only)
@crescent.event
async def on_message(event: hikari.MessageCreateEvent):
    print("Recieved an event from a human.")
```

Similar to command hooks, `HookResult` can be used to exit early from a function in a event hook.
After hooks can also be used.
