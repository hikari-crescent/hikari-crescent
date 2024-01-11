# Error Handling

The only thing exceptional is your code never throwing exceptions.
Crescent provides error handling features for commands, events, and autocomplete to solve
this problem.

Error handles can be registered for a specific exception. Creating a custom exception type for when things
are supposed to go wrong gives you a lot of control over your program.

```python
class MyError(Exception):
  ...
```

This exception can be caught.

```python

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
