import hikari

import crescent


# Create a subclass of `crescent.Mixin` and your bot impl.
# The bot impl must have the traits `RESTAware` and `EventManagerAware`.
# `CacheAware` is optional but supporting it supports more features.
# NOTE: `crescent.Mixin` must be first.
# NOTE: The `token` kwarg in the bot impl must be called `token`. If this is
# not the case a custom __init__ function is required.
class Bot(crescent.Mixin, hikari.GatewayBot):
    ...


bot = Bot("...")
