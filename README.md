# hikari-crescent
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/magpie-dev/hikari-crescent/main.svg)](https://results.pre-commit.ci/latest/github/magpie-dev/hikari-crescent/main)

A simple command handler for [Hikari](https://github.com/hikari-py/hikari).

## Features
 - Simple and intuitive API.
 - Slash, user, and message commands.
 - Error handling.

## Usage
Crescent uses signature parsing to generate your commands. Creating commands is as easy as adding typehints!

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

```python
# python 3.9 +
from typing import Annotated as Atd

# python 3.8
from typing_extensions import Annotated

@bot.include
@crescent.command
async def say(ctx: crescent.Context, word: Atd[str, "The word to say"]):
    await ctx.respond(word)
