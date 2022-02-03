# Hikari Crescent
A simple command handler for [Hikari.](https://github.com/hikari-py/hikari)


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
from typing import Annotated as Atd

@bot.include
@crescent.command
async def say(ctx: crescent.Context, word: Atd[str, "The word to say"]):
    await ctx.respond(word)
