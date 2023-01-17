from datetime import datetime

import hikari

import crescent
from crescent.ext import tasks

bot = hikari.GatewayBot(token="...")
client = crescent.Client(bot)


# Tasks are functions that are repeated after a period of time.
# Tasks start running after hikari sends the `hikari.StartedEvent` (cache is filled).


@client.include
@tasks.loop(minutes=1)
async def loop() -> None:
    print(f"Ran at {datetime.now()}")


@client.include
# Check out https://crontab.guru/ for help making cron scheduling expressions.
@tasks.cronjob("* * * * *")
async def cronjob() -> None:
    print(f"Ran at {datetime.now()}")


bot.run()
