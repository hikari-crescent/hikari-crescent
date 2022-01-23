from __future__ import annotations
from asyncio import gather
from itertools import chain

from typing import TYPE_CHECKING
from weakref import WeakValueDictionary

from hikari import UNDEFINED, CommandOption, ShardReadyEvent, Snowflake

from crescent.utils import gather_iter
from crescent.internal.app_command import AppCommand, AppCommandType
from crescent.internal.meta_struct import MetaStruct
from crescent.internal.app_command import AppCommandMeta
from crescent.utils.options import unwrap

if TYPE_CHECKING:
    from typing import Callable, Any, Awaitable, Optional, Sequence
    from hikari import Command, UndefinedOr
    from crescent.bot import Bot
    from crescent.internal.app_command import Unique


def register_command(
    callback: Callable[..., Awaitable[Any]],
    guild: Optional[Snowflake] = None,
    group: Optional[str] = None,
    sub_group: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    options: Optional[Sequence[CommandOption]] = None,
    default_permission: UndefinedOr[bool] = UNDEFINED
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

    return meta


class CommandHandler:

    __slots__: Sequence[str] = (
        "registry",
        "bot",
        "guilds",
        "application_id",
    )

    def __init__(self, bot: Bot, guilds: Sequence[Snowflake]) -> None:
        self.bot: Bot = bot
        self.guilds: Sequence[Snowflake] = guilds
        self.application_id: Optional[Snowflake] = None

        self.registry: WeakValueDictionary[
            Unique,
            MetaStruct[AppCommandMeta]
        ] = WeakValueDictionary()

    def register(self, command: MetaStruct[AppCommandMeta]) -> MetaStruct[AppCommandMeta]:
        command.metadata.app.guild_id = command.metadata.app.guild_id or self.bot.default_guild
        self.registry[command.metadata.unique] = command
        return command

    async def get_discord_commands(self) -> Sequence[AppCommand]:
        """Fetches commands from Discord"""

        commands = list(
            await self.bot.rest.fetch_application_commands(unwrap(self.application_id))
        )

        commands.extend(
            *await gather_iter(
                self.bot.rest.fetch_application_commands(
                    unwrap(self.application_id), guild=guild
                )
                for guild in self.guilds
            )
        )

        def hikari_to_crescent_command(command: Command) -> AppCommand:
            return AppCommand(
                type=AppCommandType.CHAT_INPUT,
                name=command.name,
                description=command.description,
                guild_id=command.guild_id,
                options=command.options,
                default_permission=command.default_permission,
                id=command.id,
            )

        return [
            hikari_to_crescent_command(command)
            for command in commands
        ]

    def build_commands(self) -> Sequence[AppCommand]:
        def set_guild(command: AppCommand) -> AppCommand:
            command.guild_id = command.guild_id or self.bot.default_guild
            return command

        return tuple(set_guild(app.metadata.app) for app in self.registry.values())

    async def create_application_command(self, command: AppCommand):
        await self.bot.rest.create_application_command(
            application=unwrap(self.application_id),
            name=command.name,
            description=command.description,
            guild=command.guild_id or UNDEFINED,
            options=command.options or UNDEFINED,
            default_permission=command.default_permission
        )

    async def delete_application_command(self, command: AppCommand):
        await self.bot.rest.delete_application_command(
            application=unwrap(self.application_id),
            command=unwrap(command.id),
            guild=command.guild_id or UNDEFINED
        )

    async def init(self, event: ShardReadyEvent):
        self.application_id = event.application_id
        self.guilds = self.guilds or tuple(self.bot.cache.get_guilds_view().keys())

        discord_commands = await self.get_discord_commands()
        local_commands = self.build_commands()

        to_delete = filter(
            lambda dc: not any(dc.is_same_command(lc) for lc in local_commands),
            discord_commands
        )
        to_post = list(filter(lambda lc: lc not in discord_commands, local_commands))

        await gather(*chain(
            map(self.delete_application_command, to_delete),
            map(self.create_application_command, to_post),
        ))
