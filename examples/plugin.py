import crescent


plugin = crescent.Plugin("example")


@plugin.include
@crescent.command
def plugin_command(ctx):
    pass
