from __future__ import annotations

from types import MethodType
from typing import TYPE_CHECKING, Any

from crescent import Group, Plugin, command, hook
from crescent.context.utils import support_custom_context
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


def unwrap_hooks(hooks: list[Any]):
    print(hooks)
    return [hook.__wrapped__ for hook in hooks]


def assert_all_supports_custom_ctx(hooks: list[Any]):
    for callable in hooks:
        assert f"{support_custom_context.__name__}.<locals>.inner" in str(callable)


def test_hook_order():
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

    assert_all_supports_custom_ctx(c1.metadata.hooks)
    assert_all_supports_custom_ctx(c2.metadata.hooks)
    assert_all_supports_custom_ctx(c3.metadata.hooks)
    assert_all_supports_custom_ctx(c4.metadata.hooks)
    assert_all_supports_custom_ctx(c5.metadata.hooks)
    assert_all_supports_custom_ctx(c6.metadata.hooks)

    assert unwrap_hooks(c1.metadata.hooks) == ["command", "client"]
    assert unwrap_hooks(c2.metadata.hooks) == ["command", "group", "client"]
    assert unwrap_hooks(c3.metadata.hooks) == ["command", "subgroup", "group", "client"]
    assert unwrap_hooks(c4.metadata.hooks) == ["command", "plugin", "client"]
    assert unwrap_hooks(c5.metadata.hooks) == ["command", "group", "plugin", "client"]
    assert unwrap_hooks(c6.metadata.hooks) == ["command", "subgroup", "group", "plugin", "client"]


def test_after_hook_order():
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

    assert_all_supports_custom_ctx(c1.metadata.hooks)
    assert_all_supports_custom_ctx(c2.metadata.hooks)
    assert_all_supports_custom_ctx(c3.metadata.hooks)
    assert_all_supports_custom_ctx(c4.metadata.hooks)
    assert_all_supports_custom_ctx(c5.metadata.hooks)
    assert_all_supports_custom_ctx(c6.metadata.hooks)

    assert unwrap_hooks(c1.metadata.after_hooks) == ["command", "client"]
    assert unwrap_hooks(c2.metadata.after_hooks) == ["command", "group", "client"]
    assert unwrap_hooks(c3.metadata.after_hooks) == ["command", "subgroup", "group", "client"]
    assert unwrap_hooks(c4.metadata.after_hooks) == ["command", "plugin", "client"]
    assert unwrap_hooks(c5.metadata.after_hooks) == ["command", "group", "plugin", "client"]
    assert unwrap_hooks(c6.metadata.after_hooks) == [
        "command",
        "subgroup",
        "group",
        "plugin",
        "client",
    ]


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

    assert unwrap_hooks(command_a.metadata.hooks) == unwrap_hooks(command_b.metadata.hooks)
