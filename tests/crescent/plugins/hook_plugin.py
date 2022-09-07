import crescent


class HookPlugin(crescent.Plugin):
    def __init__(self) -> None:
        self.loaded_hook_run_count = 0
        self.unloaded_hook_run_count = 0

        super().__init__()


plugin = HookPlugin()


@plugin.load_hook
def load():
    plugin.loaded_hook_run_count += 1


@plugin.unload_hook
def unload():
    plugin.unloaded_hook_run_count += 1
