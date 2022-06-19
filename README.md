# hikari-crescent

<div align="center">

![code-style-black](https://img.shields.io/badge/code%20style-black-black)
[![Mypy](https://github.com/magpie-dev/hikari-crescent/actions/workflows/mypy.yml/badge.svg)](https://github.com/magpie-dev/hikari-crescent/actions/workflows/mypy.yml)
[![Docs](https://github.com/magpie-dev/hikari-crescent/actions/workflows/pdoc_build.yml/badge.svg)](https://magpie-dev.github.io/hikari-crescent/crescent.html)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/magpie-dev/hikari-crescent/main.svg)](https://results.pre-commit.ci/latest/github/magpie-dev/hikari-crescent/main)
![Pypi](https://img.shields.io/pypi/v/hikari-crescent)

 </div>

🌕 A command handler for [Hikari](https://github.com/hikari-py/hikari) that keeps your project neat and tidy.

## Features
 - Simple and intuitive API.
 - Slash, user, and message commands.
 - Supports autocomplete.
 - Error handling for commands, events, and autocomplete.
 - Command groups.
 - Hooks to run function before or after a command (or any command from a group!)
 - Plugin system to easily split bot into different modules.
 - Makes typehinting easy.

### Links
> 📝 | [Docs](https://magpie-dev.github.io/hikari-crescent/crescent.html)<br>
> 📦 | [Pypi](https://pypi.org/project/hikari-crescent/)

## Installation
Crescent is supported in python3.8+.
```
pip install hikari-crescent
```

## Usage
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
use [class commands](https://github.com/magpie-dev/hikari-crescent/blob/main/examples/basic/command_classes.py).
Class commands allow you to declare a command similar to how you declare a dataclass. The option function takes a
type followed by the description, then optional information.

```python
@bot.include
@crescent.command(name="say")
class Say:
    word = crescent.option(str, "The word to say")

    async def callback(self, ctx: crescent.Context) -> None:
        await ctx.respond(self.word)
```

### Typing to Option Types Lookup Table 
| Type | Option Type |
|---|---|
| `str` | Text |
| `int` | Integer |
| `bool` | Boolean |
| `float` | Number |
| `hikari.User` | User |
| `hikari.Role` | Role |
| `crescent.Mentionable` | Role or User |
| Any Hikari channel type. | Channel. The options will be the channel type and its subclasses. |
| `Union[Channel Types]` (functions only) | Channel. ^ |
| `List[Channel Types]` (classes only) | Channel. ^ |

### Error Handling
Errors that are raised by a command can be handled by `crescent.catch_command`.

```python
class MyError(Exception):
    ...

@bot.include
@crescent.catch_command(MyError)
async def on_err(exc: MyError, ctx: crescent.Context) -> None:
    await ctx.respond("An error occurred while running the command.")

@bot.include
@crescent.command
async def my_command(ctx: crescent.Context):
    raise MyError()
```

### Events
```python
import hikari

@bot.include
@crescent.event
async def on_message_create(event: hikari.MessageCreateEvent):
    if event.message.author.is_bot:
        return
    await event.message.respond("Hello!")
```
Using crescent's event decorator lets you use
crescent's [event error handling system](https://github.com/magpie-dev/hikari-crescent/blob/main/examples/error_handling/basic.py#L27).

# Extensions
Crescent has 2 builtin extensions.

- [crescent-ext-cooldowns](https://github.com/magpie-dev/hikari-crescent/tree/main/examples/ext/cooldowns) - Allows you to add sliding window rate limits to your commands.
- [crescent-ext-tasks](https://github.com/magpie-dev/hikari-crescent/tree/main/examples/ext/tasks) - Schedules background tasks using loops or cronjobs.


# Support
Contact `Lunarmagpie❤#0001` on Discord or create an issue. All questions are welcome!

# Contributing
Create an issue for your feature. There aren't any guidelines right now so just don't be rude.
