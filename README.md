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
 - Error handling.

### Links
> 📝 | [Docs](https://magpie-dev.github.io/hikari-crescent/crescent.html)<br>
> 📦 | [Pypi](https://pypi.org/project/hikari-crescent/)

## Installation
Crescent is supported in python3.8+.
```
pip install hikari-crescent
````


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

Information for arguments can be provided using the `Annotated` type hint.
See [this example](https://github.com/magpie-dev/hikari-crescent/blob/main/examples/basic/basic.py) for more information.

```python
# python 3.9 +
from typing import Annotated as Atd

# python 3.8
from typing_extensions import Annotated as Atd

@bot.include
@crescent.command
async def say(ctx: crescent.Context, word: Atd[str, "The word to say"]):
    await ctx.respond(word)
```

Commands can also be inside of a sublcassed `crescent.Bot` object for an object-oriented workflow.

```python

import crescent

class Bot(crescent.Bot):

    # bot.include isn't needed in subclasses!
    @crescent.command
    async def say(self, ctx: crescent.Context, word: str):
        await ctx.respond(word)

```


# Support

Contact `Lunarmagpie❤#0001` on Discord or create an issue. All questions are welcome!

# Contributing

Create a issue for your feature. There aren't any guildlines right now so just don't be rude.
