from __future__ import annotations

from asyncio import gather
from collections import defaultdict
from inspect import iscoroutinefunction
from logging import getLogger
from typing import TYPE_CHECKING, Generic, TypeVar, cast

from hikari import (
    UNDEFINED,
    CommandOption,
    CommandType,
    ForbiddenError,
    OptionType,
    Permissions,
    Snowflake,
    UndefinedType,
)
from hikari.api import CommandBuilder

from crescent.exceptions import AlreadyRegisteredError
from crescent.internal.app_command import AppCommand, AppCommandMeta, Unique
from crescent.internal.meta_struct import MetaStruct
from crescent.utils import gather_iter, unwrap

if TYPE_CHECKING:
    from typing import Any, Awaitable, Callable, DefaultDict, Sequence

    from hikari import Snowflakeish

    from crescent.bot import Bot
    from crescent.typedefs import AutocompleteCallbackT

    T = TypeVar("T", bound="Callable[..., Awaitable[Any]]")


_log = getLogger(__name__)


def _plugin_unload_callback(self: MetaStruct[Any, Any]) -> None:
    self.app._command_handler.remove(self)


def _command_app_set_hook(self: MetaStruct[T, AppCommandMeta]) -> None:
    self.app._command_handler.register(self)


def register_command(
    callback: T,
    command_type: CommandType,
    name: str,
    guild: Snowflakeish | None = None,
    description: str | None = None,
    options: Sequence[CommandOption] | None = None,
    default_member_permissions: UndefinedType | int | Permissions = UNDEFINED,
    dm_enabled: bool = True,
    deprecated: bool = False,
    autocomplete: dict[str, AutocompleteCallbackT] = {},
) -> MetaStruct[T, AppCommandMeta]:

    if not iscoroutinefunction(callback):
        raise ValueError(f"`{callback.__name__}` must be an async function.")

    meta: MetaStruct[T, AppCommandMeta] = MetaStruct(
        callback=callback,
        app_set_hooks=[_command_app_set_hook],
        plugin_unload_hooks=[_plugin_unload_callback],
        metadata=AppCommandMeta(
            deprecated=deprecated,
            autocomplete=autocomplete,
            app=AppCommand(
                type=command_type,
                description=description,
                guild_id=guild,
                name=name,
                options=options,
                default_member_permissions=default_member_permissions,
                is_dm_enabled=dm_enabled,
            ),
        ),
    )

    return meta


_E = TypeVar("_E", bound="Callable[..., Awaitable[Any]]")


class ErrorHandler(Generic[_E]):
    __slots__: Sequence[str] = ("bot", "registry")

    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.registry: dict[type[Exception], MetaStruct[_E, Any]] = {}

    def register(self, meta: MetaStruct[_E, Any], exc: type[Exception]) -> None:
        if reg_meta := self.registry.get(exc):
            raise AlreadyRegisteredError(
                f"`{getattr(meta.callback, '__name__')}` can not catch `{exc.__name__}`."
                f" `{exc.__name__}` is already registered to"
                f" `{reg_meta.callback.__name__}`."
            )

        self.registry[exc] = meta

    def remove(self, exc: type[Exception]) -> None:
        self.registry.pop(exc)

    async def try_handle(self, exc: Exception, args: Sequence[Any]) -> bool:
        """
        Attempts to run a function to handle an exception. Returns whether the exception
        was handled.
        """
        if func := self.registry.get(exc.__class__):
            await func.callback(*args)
            return True

        return False


class CommandHandler:

    __slots__: Sequence[str] = ("registry", "bot", "guilds", "application_id")

    def __init__(self, bot: Bot, guilds: Sequence[Snowflakeish]) -> None:
        self.bot: Bot = bot
        self.guilds: Sequence[Snowflakeish] = guilds
        self.application_id: Snowflake | None = None

        self.registry: dict[
            Unique, MetaStruct["Callable[..., Awaitable[Any]]", AppCommandMeta]
        ] = {}

    def register(self, command: MetaStruct[T, AppCommandMeta]) -> MetaStruct[T, AppCommandMeta]:
        command.metadata.app.guild_id = command.metadata.app.guild_id or self.bot.default_guild
        # NOTE: T is bound to Callable[..., Awaitable[Any]], so we can cast it safely. Mypy's
        # support for TypeVars is bad, so it doesn't understand this.
        _command = cast("MetaStruct[Callable[..., Awaitable[Any]], AppCommandMeta]", command)
        self.registry[command.metadata.unique] = _command
        return command

    def remove(self, command: MetaStruct[T, AppCommandMeta]) -> None:
        self.registry.pop(command.metadata.unique)

    def build_commands(self) -> Sequence[AppCommand]:

        built_commands: dict[Unique, AppCommand] = {}

        for command in self.registry.values():
            if command.metadata.deprecated:
                continue

            elif command.metadata.sub_group:
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
                        description=unwrap(command.metadata.group).description or "No Description",
                        type=command.metadata.app.type,
                        guild_id=command.metadata.app.guild_id,
                        options=[],
                        default_member_permissions=command.metadata.app.default_member_permissions,
                        is_dm_enabled=command.metadata.app.is_dm_enabled,
                    )

                # The top-level command now exists. A subcommand group now if placed
                # inside the top-level command. This subcommand group will hold `command`.

                children = cast("list[CommandOption]", unwrap(built_commands[key].options))

                sub_command_group = CommandOption(
                    name=unwrap(command.metadata.sub_group).name,
                    description=unwrap(command.metadata.sub_group).description or "No Description",
                    type=OptionType.SUB_COMMAND_GROUP,
                    options=[],
                    is_required=False,
                )

                # This for-else makes sure that sub_command_group will hold a reference
                # to the subcommand group that we want to modify to hold `command`
                for cmd_in_children in children:
                    if (
                        cmd_in_children.name == sub_command_group.name
                        and cmd_in_children.description == sub_command_group.description
                        and cmd_in_children.type == sub_command_group.type
                    ):
                        sub_command_group = cmd_in_children
                        break
                else:
                    children.append(sub_command_group)

                cast("list[CommandOption]", sub_command_group.options).append(
                    CommandOption(
                        name=command.metadata.app.name,
                        description=unwrap(command.metadata.app.description),
                        type=OptionType.SUB_COMMAND,
                        options=command.metadata.app.options,
                        is_required=False,
                    )
                )

            elif command.metadata.group:
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
                        description=unwrap(command.metadata.group).description or "No Description",
                        type=command.metadata.app.type,
                        guild_id=command.metadata.app.guild_id,
                        options=[],
                        default_member_permissions=command.metadata.app.default_member_permissions,
                        is_dm_enabled=command.metadata.app.is_dm_enabled,
                    )

                # No checking has to be done before appending `command` since it is the
                # lowest level.
                cast("list[CommandOption]", built_commands[key].options).append(
                    CommandOption(
                        name=command.metadata.app.name,
                        description=unwrap(command.metadata.app.description),
                        type=command.metadata.app.type,
                        options=command.metadata.app.options,
                        is_required=False,
                    )
                )

            else:
                built_commands[Unique.from_meta_struct(command)] = command.metadata.app

        return tuple(built_commands.values())

    async def post_guild_commands(
        self, commands: Sequence[CommandBuilder], guild: Snowflakeish
    ) -> None:
        try:
            if self.application_id is None:
                raise AttributeError("Client `application_id` is not defined")
            await self.bot.rest.set_application_commands(
                application=self.application_id, commands=commands, guild=guild
            )
        except ForbiddenError:
            if guild in self.bot.cache.get_guilds_view().keys():
                _log.warning(
                    "Cannot post application commands to guild %s. Consider removing this"
                    " guild from the bot's `tracked_guilds` or inviting the bot with the"
                    " `application.commands` scope",
                    guild,
                )
                return
            _log.warning(
                "Cannot post application commands to guild %s. Bot is not part of the guild.",
                guild,
            )

    async def register_commands(self) -> None:
        guilds = list(self.guilds)

        commands = self.build_commands()

        command_guilds: DefaultDict[Snowflakeish, list[AppCommand]] = defaultdict(list)
        global_commands: list[AppCommand] = []

        for command in commands:
            if command.guild_id:
                command_guilds[command.guild_id].append(command)
                if command.guild_id in guilds:
                    guilds.remove(command.guild_id)
            else:
                global_commands.append(command)

        assert self.application_id is not None
        await gather(
            self.bot.rest.set_application_commands(
                application=self.application_id, commands=global_commands
            ),
            gather_iter(
                self.post_guild_commands(commands, guild)
                for guild, commands in command_guilds.items()
            ),
            gather_iter(
                self.bot.rest.set_application_commands(
                    application=self.application_id, commands=[], guild=guild
                )
                for guild in guilds
            ),
        )
