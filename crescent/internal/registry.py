from __future__ import annotations

from asyncio import gather
from inspect import iscoroutinefunction
from itertools import chain
from logging import getLogger
from typing import TYPE_CHECKING, cast
from weakref import WeakValueDictionary

from hikari import (
    UNDEFINED,
    CommandOption,
    CommandType,
    ForbiddenError,
    OptionType,
    SlashCommand,
    Snowflake,
    Snowflakeish,
)

from crescent.internal.app_command import AppCommand, AppCommandMeta, Unique
from crescent.internal.meta_struct import MetaStruct
from crescent.utils import gather_iter
from crescent.utils.options import unwrap

if TYPE_CHECKING:
    from typing import Any, Awaitable, Callable, Dict, List, Optional, Sequence, Type

    from hikari import PartialCommand, UndefinedOr

    from crescent.bot import Bot
    from crescent.typedefs import CommandCallbackT
    from crescent.commands.errors import _ErrorHandlerCallback


_log = getLogger(__name__)


def register_command(
    callback: Callable[..., Awaitable[Any]],
    command_type: CommandType,
    name: str,
    guild: Optional[Snowflakeish] = None,
    description: Optional[str] = None,
    options: Optional[Sequence[CommandOption]] = None,
    default_permission: UndefinedOr[bool] = UNDEFINED,
) -> MetaStruct[CommandCallbackT, AppCommandMeta]:

    if not iscoroutinefunction(callback):
        raise ValueError(f"`{callback.__name__}` must be an async function.")

    description = description or "\u200B"

    def hook(self: MetaStruct[CommandCallbackT, AppCommandMeta]) -> None:
        self.app._command_handler.register(self)

    meta: MetaStruct[CommandCallbackT, AppCommandMeta] = MetaStruct(
        callback=callback,
        app_set_hooks=[hook],
        metadata=AppCommandMeta(
            app=AppCommand(
                type=command_type,
                description=description,
                guild_id=guild,
                name=name,
                options=options,
                default_permission=default_permission,
            )
        ),
    )

    return meta


class ErrorHandler:
    __slots__: Sequence[str] = ("bot", "registry")

    def __init__(self, bot: Bot):
        self.bot = bot
        self.registry: Dict[Type[Exception], List[MetaStruct[_ErrorHandlerCallback, Any]]] = {}


class CommandHandler:

    __slots__: Sequence[str] = ("registry", "bot", "guilds", "application_id")

    def __init__(self, bot: Bot, guilds: Sequence[Snowflakeish]) -> None:
        self.bot: Bot = bot
        self.guilds: Sequence[Snowflakeish] = guilds
        self.application_id: Optional[Snowflake] = None

        self.registry: WeakValueDictionary[
            Unique, MetaStruct[CommandCallbackT, AppCommandMeta]
        ] = WeakValueDictionary()

    def register(
        self, command: MetaStruct[CommandCallbackT, AppCommandMeta]
    ) -> MetaStruct[CommandCallbackT, AppCommandMeta]:
        command.metadata.app.guild_id = command.metadata.app.guild_id or self.bot.default_guild
        self.registry[command.metadata.unique] = command
        return command

    async def get_discord_commands(self) -> Sequence[AppCommand]:
        """Fetches commands from Discord"""

        res_commands = list(
            await self.bot.rest.fetch_application_commands(unwrap(self.application_id))
        )

        async def fetch_guild_app_command(guild: Snowflakeish):
            try:
                return await self.bot.rest.fetch_application_commands(
                    unwrap(self.application_id), guild=guild
                )
            except ForbiddenError:
                _log.warning(
                    "Cannot access application commands for guild %s. Consider "
                    " removing this guild from the bot's `tracked_guilds` or inviting"
                    " the bot with the `application.commands` scope.",
                    guild,
                )

        guild_commands = await gather_iter(fetch_guild_app_command(guild) for guild in self.guilds)

        for commands in guild_commands:
            if commands is None:
                continue
            res_commands.extend(commands)

        def hikari_to_crescent_command(command: PartialCommand) -> AppCommand:
            if isinstance(command, SlashCommand):
                return AppCommand(
                    type=command.type,
                    name=command.name,
                    description=command.description,
                    guild_id=command.guild_id,
                    options=command.options,
                    default_permission=command.default_permission,
                    id=command.id,
                )
            return AppCommand(
                type=command.type,
                name=command.name,
                guild_id=command.guild_id,
                default_permission=command.default_permission,
                id=command.id,
            )

        return [hikari_to_crescent_command(command) for command in res_commands]

    def build_commands(self) -> Sequence[AppCommand]:

        built_commands: Dict[Unique, AppCommand] = {}

        for command in self.registry.values():
            command.metadata.app.guild_id = command.metadata.app.guild_id or self.bot.default_guild

            if command.metadata.sub_group:
                # If a command has a sub_group, it must be nested 2 levels deep.
                #
                # command
                #     subcommand-group
                #         subcommand
                #
                # The children of the subcommand-group object are being set to include
                # `command` If that subcommand-group object does not exist, it will be
                # created here. The same goes for the top-level command.
                #
                # First make sure the command exists. This command will hold the
                # subcommand-group for `command`.

                # `key` represents the unique value for the top-level command that will
                # hold the subcommand.
                key = Unique(
                    name=unwrap(command.metadata.group).name,
                    type=command.metadata.app.type,
                    guild_id=command.metadata.app.guild_id,
                    group=None,
                    sub_group=None,
                )

                if key not in built_commands:
                    built_commands[key] = AppCommand(
                        name=unwrap(command.metadata.group).name,
                        description=unwrap(command.metadata.group).description or "\u200B",
                        type=command.metadata.app.type,
                        guild_id=command.metadata.app.guild_id,
                        options=[],
                        default_permission=command.metadata.app.default_permission,
                    )

                # The top-level command now exists. A subcommand group now if placed
                # inside the top-level command. This subcommand group will hold `command`.

                children = unwrap(built_commands[key].options)

                sub_command_group = CommandOption(
                    name=unwrap(command.metadata.sub_group).name,
                    description=unwrap(command.metadata.sub_group).description or "\u200B",
                    type=OptionType.SUB_COMMAND_GROUP,
                    options=[],
                    is_required=None,  # type: ignore
                )

                # This for-else makes sure that sub_command_group will hold a reference
                # to the subcommand group that we want to modify to hold `command`
                for cmd_in_children in children:
                    if all(
                        (
                            cmd_in_children.name == sub_command_group.name,
                            cmd_in_children.description == sub_command_group.description,
                            cmd_in_children.type == sub_command_group.type,
                        )
                    ):
                        sub_command_group = cmd_in_children
                        break
                else:
                    cast(list, children).append(sub_command_group)

                cast(list, sub_command_group.options).append(
                    CommandOption(
                        name=command.metadata.app.name,
                        description=unwrap(command.metadata.app.description),
                        type=OptionType.SUB_COMMAND,
                        options=command.metadata.app.options,
                        is_required=None,  # type: ignore
                    )
                )

                continue

            if command.metadata.group:
                # Any command at this point will only have one level of nesting.
                #
                # Command
                #    subcommand
                #
                # A subcommand object is what is being generated here. If there is no
                # top level command, it will be created here.

                # `key` represents the unique value for the top-level command that will
                # hold the subcommand.
                key = Unique(
                    name=command.metadata.group.name,
                    type=command.metadata.app.type,
                    guild_id=command.metadata.app.guild_id,
                    group=None,
                    sub_group=None,
                )

                if key not in built_commands:
                    built_commands[key] = AppCommand(
                        name=command.metadata.group.name,
                        description="HIDDEN",
                        type=command.metadata.app.type,
                        guild_id=command.metadata.app.guild_id,
                        options=[],
                        default_permission=command.metadata.app.default_permission,
                    )

                # No checking has to be done before appending `command` since it is the
                # lowest level.
                cast(list, built_commands[key].options).append(
                    CommandOption(
                        name=command.metadata.app.name,
                        description=unwrap(command.metadata.app.description),
                        type=command.metadata.app.type,
                        options=command.metadata.app.options,
                        is_required=None,  # type: ignore
                    )
                )

                continue

            built_commands[Unique.from_meta_struct(command)] = command.metadata.app

        return tuple(built_commands.values())

    async def create_application_command(self, command: AppCommand):
        try:
            if command.type in {CommandType.MESSAGE, CommandType.USER}:
                await self.bot.rest.create_context_menu_command(
                    application=unwrap(self.application_id),
                    type=command.type,  # type: ignore
                    name=command.name,
                    guild=command.guild_id or UNDEFINED,
                    default_permission=command.default_permission,
                )
                return
            await self.bot.rest.create_slash_command(
                application=unwrap(self.application_id),
                name=command.name,
                description=unwrap(command.description),
                guild=command.guild_id or UNDEFINED,
                options=command.options or UNDEFINED,
                default_permission=command.default_permission,
            )
        except ForbiddenError:
            if command.guild_id in self.bot.cache.get_guilds_view().keys():
                _log.warning(
                    "Cannot post application command `%s` to guild %s. Consider removing this"
                    " guild from the bot's `tracked_guilds` or inviting the bot with the"
                    " `application.commands` scope",
                    command.name,
                    command.guild_id,
                )
                return
            _log.warning(
                "Cannot post application command `%s` to guild %s. Bot is not part of the guild.",
                command.name,
                command.guild_id,
            )

    async def delete_application_command(self, command: AppCommand):
        await self.bot.rest.delete_application_command(
            application=unwrap(self.application_id),
            command=unwrap(command.id),
            guild=command.guild_id or UNDEFINED,
        )

    async def register_commands(self):
        self.guilds = self.guilds or tuple(self.bot.cache.get_guilds_view().keys())

        discord_commands = await self.get_discord_commands()
        local_commands = self.build_commands()

        to_delete = filter(
            lambda dc: not any(dc.is_same_command(lc) for lc in local_commands), discord_commands
        )
        to_post = list(filter(lambda lc: lc not in discord_commands, local_commands))

        await gather(
            *chain(
                map(self.delete_application_command, to_delete),
                map(self.create_application_command, to_post),
            )
        )
