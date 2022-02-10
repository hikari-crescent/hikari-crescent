from __future__ import annotations

from asyncio import gather
from collections import defaultdict
from inspect import iscoroutinefunction
from logging import getLogger
from typing import TYPE_CHECKING, cast
from weakref import WeakValueDictionary

from hikari import UNDEFINED, CommandOption, CommandType, ForbiddenError, OptionType, Snowflake
from hikari.api import CommandBuilder

from crescent.internal.app_command import AppCommand, AppCommandMeta, Unique
from crescent.internal.meta_struct import MetaStruct
from crescent.utils import gather_iter, unwrap

if TYPE_CHECKING:
    from typing import Any, Awaitable, Callable, DefaultDict, Dict, List, Optional, Sequence, Type

    from hikari import Snowflakeish, UndefinedOr

    from crescent.bot import Bot
    from crescent.commands.errors import _InternalErrorHandlerCallbackT
    from crescent.typedefs import CommandCallbackT


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
        self.registry: WeakValueDictionary[
            Type[Exception], MetaStruct[_InternalErrorHandlerCallbackT, Any]
        ] = WeakValueDictionary()


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
                        description=unwrap(command.metadata.group).description or "\u200B",
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

    async def post_guild_command(self, commands: List[CommandBuilder], guild: Snowflakeish):
        try:
            if not self.application_id:
                raise AttributeError("Client `application_id` is not defined")
            await self.bot.rest.set_application_commands(
                application=self.application_id, commands=commands, guild=guild
            )
        except ForbiddenError:
            if guild in self.bot.cache.get_guilds_view().keys():
                _log.warning(
                    "Cannot post application commands to guild %s. Consider removing this"
                    " guild from the bot's `tracked_guilds` or inviting the bot with the"
                    " `application.commands` scope"
                )
                return
            _log.warning(
                "Cannot post application commands to guild %s. Bot is not part of the guild."
            )

    async def register_commands(self):
        guilds = list(self.guilds) or list(self.bot.cache.get_guilds_view().keys())

        commands = self.build_commands()

        command_guilds: DefaultDict[Snowflakeish, List[AppCommand]] = defaultdict(list)
        global_commands: List[AppCommand] = []

        for command in commands:
            if command.guild_id:
                command_guilds[command.guild_id].append(command)
                if command.guild_id in guilds:
                    guilds.remove(command.guild_id)
            else:
                global_commands.append(command)

        await gather(
            self.bot.rest.set_application_commands(
                application=self.application_id, commands=global_commands
            ),
            gather_iter(
                self.post_guild_command(commands, guild)
                for guild, commands in command_guilds.items()
            ),
            gather_iter(
                self.bot.rest.set_application_commands(
                    application=self.application_id, commands=[], guild=guild
                )
                for guild in guilds
            ),
        )
