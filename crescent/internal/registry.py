from __future__ import annotations
from asyncio import sleep

from typing import TYPE_CHECKING
from weakref import WeakValueDictionary

from hikari import ShardReadyEvent, Snowflake

from crescent.internal.app_command import AppCommand, AppCommandOption, AppCommandType
from crescent.internal.meta_struct import MetaStruct
from crescent.internal.app_command import AppCommandMeta

if TYPE_CHECKING:
    from typing import Callable, Any, Awaitable, Optional, Sequence
    from crescent.bot import Bot


def register_command(
    callback: Callable[..., Awaitable[Any]],
    guild: Optional[Snowflake] = None,
    name: Optional[str] = None,
    group: Optional[str] = None,
    sub_group: Optional[str] = None,
    description: Optional[str] = None,
    options: Optional[Sequence[AppCommandOption]] = None,
    default_permission: Optional[bool] = None
):

    name = name or callback.__name__
    description = description or "No Description Set"

    meta: MetaStruct[AppCommandMeta] = MetaStruct(
        callback=callback,
        manager=None,
        metadata=AppCommandMeta(
            group=group,
            sub_group=sub_group,
            app=AppCommand(
                type=AppCommandType.CHAT_INPUT,
                description=description,
                guild_id=guild,
                name=name,
                options=options,
                default_permission=default_permission
            )
        )
    )

    CommandHandler.register[meta.metadata.unique] = meta

    return meta


class CommandHandler:
    register: WeakValueDictionary[
        int,
        MetaStruct[AppCommandMeta]
    ] = WeakValueDictionary()

    @classmethod
    async def init(cls, me: Bot, guilds, event: ShardReadyEvent):
        application_id = event.application_id
        guilds = guilds or me.cache.get_guilds_view().keys()
