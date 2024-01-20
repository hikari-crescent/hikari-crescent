# Tasks

This module allows you to loop functions on a certain time period.

## Loops

Loops run a certain time period after you start the bot.

Using kwargs, functions can be set to loop after a certain amount of hours, minutes,
or seconds.

```python
from crescent.ext import tasks
from datetime import datetime

# This function runs once every minute.
@client.include
@tasks.loop(hours=0, minutes=1, seconds=0)
async def loop():
    print(datetime.now())
```

A `datetime.timedelta` object can be passed in to `tasks.loop` for more control
over when the function loops.

```python
from crescent.ext import tasks
from datetime import datetime, timedelta

# This function runs once every day.
@client.include
@tasks.loop(timedelta(days=1))
async def loop():
    print(datetime.now())
```


## Cronjobs

Cronjobs are supported with the `tasks.cronjob` function.
[crontab.guru](https://crontab.guru/) is useful for writing cron expressions.

!!! info
        
    The library [croniter](https://pypi.org/project/croniter/) is used for parsing cron expressions.

```python
from crescent.ext import tasks
from datetime import datetime

# This function runs once every minute.
@client.include
@tasks.cronjob("* * * * *")
async def loop():
    print(datetime.now())
```

The `on_startup=True` can be set to force the function to run when the bot is started.

```python
@client.include
@tasks.cronjob("* * * * *", on_startup=True)
async def loop():
    print(datetime.now())
```
