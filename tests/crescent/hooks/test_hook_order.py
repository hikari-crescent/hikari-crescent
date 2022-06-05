from __future__ import annotations

from types import MethodType
from typing import TYPE_CHECKING, Any

from crescent import Bot, Group, Plugin, command, hook


async def async_func(*a, **k) -> None:
    ...


class _MockHook:
    def __init__(self, name: str) -> None:
        self.name = name
        self.__name__ = name

    __repr__ = __str__ = lambda self: self.name

    __class__ = MethodType
    __func__ = async_func

    def __eq__(self, ot: object) -> bool:
        return self.name == ot


if TYPE_CHECKING:
    MockHook = Any
else:
    MockHook = _MockHook


def test_hook_order():
    bot = Bot("NO TOKEN", command_hooks=[MockHook("bot")])
    plugin = Plugin("PLUGIN", command_hooks=[MockHook("plugin")])
    group = Group("BOT_GROUP", hooks=[MockHook("group")])
    subgroup = group.sub_group("SUBGROUP", hooks=[MockHook("subgroup")])

    @bot.include
    @hook(MockHook("command"))
    @command
    async def c1(ctx) -> None:
        ...

    @bot.include
    @hook(MockHook("command"))
    @group.child
    @command
    async def c2(ctx) -> None:
        ...

    @bot.include
    @hook(MockHook("command"))
    @subgroup.child
    @command
    async def c3(ctx) -> None:
        ...

    @plugin.include
    @hook(MockHook("command"))
    @command
    async def c4(ctx) -> None:
        ...  # *pytest explodes*

    @plugin.include
    @hook(MockHook("command"))
    @group.child
    @command
    async def c5(ctx) -> None:
        ...

    @plugin.include
    @hook(MockHook("command"))
    @subgroup.child
    @command
    async def c6(ctx) -> None:
        ...

    bot.plugins.add_plugin(plugin)

    assert c1.metadata.hooks == ["command", "bot"]
    assert c2.metadata.hooks == ["command", "group", "bot"]
    assert c3.metadata.hooks == ["command", "subgroup", "group", "bot"]
    assert c4.metadata.hooks == ["command", "plugin", "bot"]
    assert c5.metadata.hooks == ["command", "group", "plugin", "bot"]
    assert c6.metadata.hooks == ["command", "subgroup", "group", "plugin", "bot"]


def test_after_hook_order():
    bot = Bot("NO TOKEN", command_after_hooks=[MockHook("bot")])
    plugin = Plugin("PLUGIN", command_after_hooks=[MockHook("plugin")])
    group = Group("BOT_GROUP", hook_after=[MockHook("group")])
    subgroup = group.sub_group("SUBGROUP", hook_after=[MockHook("subgroup")])

    @bot.include
    @hook(MockHook("command"), after=True)
    @command
    async def c1(ctx) -> None:
        ...

    @bot.include
    @hook(MockHook("command"), after=True)
    @group.child
    @command
    async def c2(ctx) -> None:
        ...

    @bot.include
    @hook(MockHook("command"), after=True)
    @subgroup.child
    @command
    async def c3(ctx) -> None:
        ...

    @plugin.include
    @hook(MockHook("command"), after=True)
    @command
    async def c4(ctx) -> None:
        ...  # *pytest explodes*

    @plugin.include
    @hook(MockHook("command"), after=True)
    @group.child
    @command
    async def c5(ctx) -> None:
        ...

    @plugin.include
    @hook(MockHook("command"), after=True)
    @subgroup.child
    @command
    async def c6(ctx) -> None:
        ...

    bot.plugins.add_plugin(plugin)

    assert c1.metadata.after_hooks == ["command", "bot"]
    assert c2.metadata.after_hooks == ["command", "group", "bot"]
    assert c3.metadata.after_hooks == ["command", "subgroup", "group", "bot"]
    assert c4.metadata.after_hooks == ["command", "plugin", "bot"]
    assert c5.metadata.after_hooks == ["command", "group", "plugin", "bot"]
    assert c6.metadata.after_hooks == ["command", "subgroup", "group", "plugin", "bot"]
