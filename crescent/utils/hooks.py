from __future__ import annotations

from typing import Any, Protocol, Sequence

from crescent.internal.app_command import AppCommandMeta
from crescent.internal.meta_struct import MetaStruct
from crescent.typedefs import HookCallbackT

__all__: Sequence[str] = ("add_hooks",)


class HasHooks(Protocol):
    command_hooks: list[HookCallbackT] | None
    command_after_hooks: list[HookCallbackT] | None


def add_hooks(obj: HasHooks, command: MetaStruct[Any, Any]) -> None:
    if not isinstance(command.metadata, AppCommandMeta):
        return
    if obj.command_hooks:
        command.metadata.hooks.extend(obj.command_hooks)
    if obj.command_after_hooks:
        command.metadata.after_hooks.extend(obj.command_after_hooks)
