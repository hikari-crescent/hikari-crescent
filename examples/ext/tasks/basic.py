from datetime import datetime

import crescent
from crescent.ext import tasks

bot = crescent.Bot("...")


# Tasks are functions that are repeated after a period of time.
# Tasks start running after hikari sends the `hikari.StartedEvent` (cache is filled).


@bot.include
@tasks.loop(minutes=1)
async def loop() -> None:
    print(f"Ran at {datetime.now()}")


@bot.include
# Check out https://crontab.guru/ for help making cron scheduling expressions.
@tasks.cronjob("* * * * *")
async def cronjob() -> None:
    print(f"Ran at {datetime.now()}")


bot.run()
