from __future__ import annotations

from types import MethodType
from typing import TYPE_CHECKING, Any

from crescent import Group, Plugin, command, hook, event
from hikari import Event
from tests.utils import MockClient


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

    def __call__(self):
        ...

    def __hash__(self) -> int:
        return 0


if TYPE_CHECKING:
    MockHook = Any
else:
    MockHook = _MockHook


def test_command_hook_order():
    client = MockClient(command_hooks=[MockHook("client")])
    plugin = Plugin(command_hooks=[MockHook("plugin")])
    group = Group("BOT_GROUP", hooks=[MockHook("group")])
    subgroup = group.sub_group("SUBGROUP", hooks=[MockHook("subgroup")])

    @client.include
    @hook(MockHook("command"))
    @command
    async def c1(ctx) -> None:
        ...

    @client.include
    @hook(MockHook("command"))
    @group.child
    @command
    async def c2(ctx) -> None:
        ...

    @client.include
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

    client.plugins._add_plugin("", plugin)

    assert c1.metadata.hooks == ["command", "client"]
    assert c2.metadata.hooks == ["command", "group", "client"]
    assert c3.metadata.hooks == ["command", "subgroup", "group", "client"]
    assert c4.metadata.hooks == ["command", "plugin", "client"]
    assert c5.metadata.hooks == ["command", "group", "plugin", "client"]
    assert c6.metadata.hooks == ["command", "subgroup", "group", "plugin", "client"]


def test_command_after_hook_order():
    client = MockClient("NO TOKEN", command_after_hooks=[MockHook("client")])
    plugin = Plugin(command_after_hooks=[MockHook("plugin")])
    group = Group("BOT_GROUP", after_hooks=[MockHook("group")])
    subgroup = group.sub_group("SUBGROUP", after_hooks=[MockHook("subgroup")])

    @client.include
    @hook(MockHook("command"), after=True)
    @command
    async def c1(ctx) -> None:
        ...

    @client.include
    @hook(MockHook("command"), after=True)
    @group.child
    @command
    async def c2(ctx) -> None:
        ...

    @client.include
    @hook(MockHook("command"), after=True)
    @subgroup.child
    @command
    async def c3(ctx) -> None:
        ...

    @plugin.include
    @hook(MockHook("command"), after=True)
    @command
    async def c4(ctx) -> None:
        ...

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

    client.plugins._add_plugin("", plugin)

    assert c1.metadata.after_hooks == ["command", "client"]
    assert c2.metadata.after_hooks == ["command", "group", "client"]
    assert c3.metadata.after_hooks == ["command", "subgroup", "group", "client"]
    assert c4.metadata.after_hooks == ["command", "plugin", "client"]
    assert c5.metadata.after_hooks == ["command", "group", "plugin", "client"]
    assert c6.metadata.after_hooks == ["command", "subgroup", "group", "plugin", "client"]


def test_vargs_hooks():
    @hook(MockHook("a"))
    @hook(MockHook("b"))
    @hook(MockHook("c"))
    @command
    async def command_a(ctx):
        ...

    @hook(MockHook("a"), MockHook("b"), MockHook("c"))
    @command
    async def command_b(ctx):
        ...

    assert command_a.metadata.hooks == command_b.metadata.hooks


def test_event_hook_order():
    client = MockClient(event_hooks=[MockHook("client")])
    plugin = Plugin(event_hooks=[MockHook("plugin")])

    @client.include
    @hook(MockHook("command"))
    @event
    async def e1(event: Event) -> None:
        ...

    @plugin.include
    @hook(MockHook("command"))
    @event
    async def e2(event: Event) -> None:
        ...

    client.plugins._add_plugin("", plugin)

    assert e1.metadata.hooks == ["command", "client"]
    assert e2.metadata.hooks == ["command", "plugin", "client"]


def test_event_after_hook_order():
    client = MockClient("NO TOKEN", event_after_hooks=[MockHook("client")])
    plugin = Plugin(event_after_hooks=[MockHook("plugin")])

    @client.include
    @hook(MockHook("command"), after=True)
    @event
    async def e1(event: Event) -> None:
        ...

    @plugin.include
    @hook(MockHook("command"), after=True)
    @event
    async def e2(event: Event) -> None:
        ...

    client.plugins._add_plugin("", plugin)

    assert e1.metadata.after_hooks == ["command", "client"]
    assert e2.metadata.after_hooks == ["command", "plugin", "client"]
