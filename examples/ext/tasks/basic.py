from datetime import datetime

import crescent
from crescent.ext import tasks

bot = crescent.Bot("...")

# Check out https://crontab.guru/ for help making cron expressions


@bot.include
@tasks.cronjob("* * * * *")
async def job():
    print(f"Ran at {datetime.now()}")
