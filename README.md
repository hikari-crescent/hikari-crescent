# hikari-crescent

<div align="center">

![code-style-black](https://img.shields.io/badge/code%20style-black-black)
[![Mypy](https://github.com/magpie-dev/hikari-crescent/actions/workflows/mypy.yml/badge.svg)](https://github.com/magpie-dev/hikari-crescent/actions/workflows/mypy.yml)
[![Docs](https://github.com/magpie-dev/hikari-crescent/actions/workflows/pdoc.yml/badge.svg)](https://magpie-dev.github.io/hikari-crescent/crescent.html)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/magpie-dev/hikari-crescent/main.svg)](https://results.pre-commit.ci/latest/github/magpie-dev/hikari-crescent/main)
![Pypi](https://img.shields.io/pypi/v/hikari-crescent)

 </div>
 
A simple command handler for [Hikari](https://github.com/hikari-py/hikari).

## Features
 - Simple and intuitive API.
 - Slash, user, and message commands.
 - Error handling for commands, events, and autocomplete.
 - Command groups.
 - Hooks to run function before a command (or any command from a group!)
 - Plugin system to easily split bot into different modules.
 - Typing is easy.

### Links
> 📝 | [Docs](https://magpie-dev.github.io/hikari-crescent/crescent.html)<br>
> 📦 | [Pypi](https://pypi.org/project/hikari-crescent/)

## Installation
Crescent is supported in python3.8+.
```
pip install hikari-crescent
```

# Usage
Signature parsing can be used for simple commands.

```python
import crescent

bot = crescent.Bot("YOUR_TOKEN")

# Include the command in your bot - don't forget this
@bot.include
# Create a slash command
@crescent.command
async def say(ctx: crescent.Context, word: str):
    await ctx.respond(word)

bot.run()
```

Information for arguments can be provided using the `Annotated` type hint.
See [this example](https://github.com/magpie-dev/hikari-crescent/blob/main/examples/basic/basic.py) for more information.

```python
# python 3.9 +
from typing import Annotated as Atd

# python 3.8
from typing_extensions import Annotated as Atd

@bot.include
@crescent.command
async def say(ctx: crescent.Context, word: Atd[str, "The word to say"]) -> None:
    await ctx.respond(word)
```

Complicated commands, such as commands with many modifiers on options or autocomplete on several options, should
use the class command system. Class commands allow you to declare a command similar to how you
declare a dataclass. The option function takes a type followed by the description then optional
information.

```python
@bot.include
@crescent.command(name="say")
class Say:
    word = crescent.option(str, "The word to say")

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.respond(self.word)
```

## Error Handling
Errors that are raised by a command can be handled by `crescent.catch_command`.

```python
class MyError(Exception):
    ...

@bot.include
@crescent.catch_command(MyError)
async def on_err(exc: MyError, ctx: crescent.Context) -> None:
    await ctx.respond("There was an error while running the command.")

@bot.include
@crescent.command
async def my_command(ctx: crescent.Context):
    raise MyError()
```

## Events
```python
import hikari

@bot.include
@crescent.event
async def on_message_create(event: hikari.MessageCreateEvent):
    if event.message.author.is_bot:
        return
    await event.message.respond("Hello!")
```
Using crescent's event decorator allows you to access crescent's [event error handling system](https://github.com/magpie-dev/hikari-crescent/blob/main/examples/error_handling/basic.py#L27).

# Support
Contact `Lunarmagpie❤#0001` on Discord or create an issue. All questions are welcome!

# Contributing
Create a issue for your feature. There aren't any guildlines right now so just don't be rude.
