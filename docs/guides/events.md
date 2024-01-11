# Events

Events are the main driving force behind Gateway bots. Whenever "something" happens on Discord that
your bot should be notified of, Discord will send an event.

Although hikari provides `hikari.GatewayBot.subscribe` you should NOT use this function. Crescent's method
of subscribing to events will work in plugins and will allow you to take advantage of [error handling](../error_handling).

The `@crescent.event` decorator is used to subscribe to an event. The type hint for `event` is the event
type from hikari you want to subscribe to. This must be a subtype of [`hikari.Event`][hikari.events.base_events.Event].

```python
import hikari

@client.include
@crescent.event
async def on_message_create(event: hikari.MessageCreateEvent):
    if event.message.author.is_bot:
        return
    await event.message.respond("Hello!")
```
