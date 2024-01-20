# Error Handling

The only thing exceptional is your code never throwing exceptions.
Crescent provides error handling features for commands, events, and autocomplete to solve
this problem.

Error handles can be registered for a specific exception. Creating a custom exception type for when things
are supposed to go wrong gives you a lot of control over your program.

This error will be handled with the [`@crescent.catch_command`][crescent.errors.catch_command] decorator.
This function takes an exception and [`crescent.Context`][crescent.context.Context] as an argument. All subclasses of the exception will be caught.

```python
# Creating a new error class gives more control over what errors are handled.
class MyError(Exception):
  ...

@client.include
@crescent.command
async def my_command(ctx: crescent.Context, number: int):
  # Lets raise an error if the number wasn't positive.
  if number < 0:
    raise MyError
  await ctx.reply(str(number))


# Handle the error
@client.include
@crescent.catch_command(MyError)
# The name of this function does not matter.
async def on_cmd_my_error(exc: MyError, ctx: crescent.Context) -> None:
    await ctx.respond(f"{exc} raised in {ctx.command}!")
```

Event and autocomplete error handling works similar to command error handling.

```python
@client.include
@crescent.catch_event(MyError)
async def on_event_random_error(exc: MyError, event: hikari.Event) -> None:
    # In this example, we don't respond to the event if something went wrong.
    print(f"{exc} raised in {event}!")

@client.include
@crescent.catch_autocomplete(MyError)
async def on_autocomplete_random_error(
    exc: MyError,
    ctx: crescent.AutocompleteContext,
    inter: hikari.AutocompleteInteractionOption,
) -> None:
    print(f"{exc} raised in autocomplete for {ctx.command}!")
```

Note that error handling can catch errors from other plugins. If you want to catch an error specific to a plugin
the best method to do this is creating a new exception type, only referenced in that plugin.

## Handling All Exceptions

A global error handler can be created by catch [`Exception`][Exception].

```python
@client.include
@crescent.catch_command(Exception)
async def global_error_handler(exc: Exception, ctx: crescent.Context):
    await ctx.respond("handled")
```

The same method can be used with event error handlers and autocomplete error handlers.
