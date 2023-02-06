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
from hikari.traits import CacheAware

from crescent.context.utils import support_custom_context
from crescent.exceptions import AlreadyRegisteredError
from crescent.internal.app_command import AppCommand, AppCommandMeta, Unique
from crescent.internal.includable import Includable
from crescent.locale import LocaleBuilder, str_or_build_locale
from crescent.utils import gather_iter, unwrap

if TYPE_CHECKING:
    from typing import Any, Awaitable, Callable, DefaultDict, Iterable, Sequence

    from hikari import PartialGuild, Snowflakeish, SnowflakeishOr

    from crescent.client import Client
    from crescent.typedefs import AutocompleteCallbackT, CanBuild, CommandCallbackT

    T = TypeVar("T", bound="Callable[..., Awaitable[Any]]")

_log = getLogger(__name__)


def _plugin_unload_callback(self: Includable[Any]) -> None:
    self.client._command_handler._remove(self)


def _command_client_set_hook(self: Includable[AppCommandMeta]) -> None:
    self.client._command_handler._register(self)


def register_command(
    owner: Any,
    callback: CommandCallbackT,
    command_type: CommandType,
    name: str | LocaleBuilder,
    guild: Snowflakeish | None = None,
    description: str | LocaleBuilder | None = None,
    options: Sequence[CommandOption] | None = None,
    default_member_permissions: UndefinedType | int | Permissions = UNDEFINED,
    dm_enabled: bool = True,
    autocomplete: dict[str, AutocompleteCallbackT] = {},
    nsfw: bool | None = None,
) -> Includable[AppCommandMeta]:
    if not iscoroutinefunction(callback):
        raise ValueError(f"`{callback.__name__}` must be an async function.")

    includable: Includable[AppCommandMeta] = Includable(
        client_set_hooks=[_command_client_set_hook],
        plugin_unload_hooks=[_plugin_unload_callback],
        metadata=AppCommandMeta(
            owner=owner,
            callback=support_custom_context(callback),
            autocomplete={k: support_custom_context(v) for k, v in autocomplete.items()},
            app_command=AppCommand(
                type=command_type,
                description=description,
                guild_id=guild,
                name=name,
                options=options,
                default_member_permissions=default_member_permissions,
                is_dm_enabled=dm_enabled,
                nsfw=nsfw,
            ),
        ),
    )

    return includable


_E = TypeVar("_E", bound="Callable[..., Awaitable[Any]]")


class ErrorHandler(Generic[_E]):
    __slots__: Sequence[str] = ("bot", "registry", "supports_custom_ctx")

    def __init__(self) -> None:
        self.registry: dict[type[Exception], Includable[_E]] = {}

    def register(self, includable: Includable[_E], exc: type[Exception]) -> None:
        if reg_includable := self.registry.get(exc):
            raise AlreadyRegisteredError(
                f"`{getattr(includable.metadata, '__name__')}` can not catch `{exc.__name__}`."
                f" `{exc.__name__}` is already registered to"
                f" `{reg_includable.metadata.__name__}`."
            )

        self.registry[exc] = includable

    def remove(self, exc: type[Exception]) -> None:
        self.registry.pop(exc)

    async def try_handle(self, exc: Exception, args: Sequence[Any]) -> bool:
        """
        Attempts to run a function to handle an exception. Returns whether the exception
        was handled.
        """
        if func := self.registry.get(exc.__class__):
            await func.metadata(*args)
            return True

        return False


class CommandHandler:
    __slots__: Sequence[str] = ("_client", "_guilds", "_application_id", "_registry")

    def __init__(self, client: Client, guilds: Sequence[Snowflakeish]) -> None:
        self._client: Client = client
        self._guilds: Sequence[Snowflakeish] = guilds
        self._application_id: Snowflake | None = None

        self._registry: dict[Unique, Includable[AppCommandMeta]] = {}

    def _register(self, command: Includable[AppCommandMeta]) -> Includable[AppCommandMeta]:
        command.metadata.app_command.guild_id = (
            command.metadata.app_command.guild_id or self._client.default_guild
        )
        self._registry[command.metadata.unique] = command
        return command

    def _remove(self, command: Includable[AppCommandMeta]) -> None:
        self._registry.pop(command.metadata.unique)

    def _get(self, unique: Unique) -> Includable[AppCommandMeta]:
        return self._registry[unique]

    def __build_commands(self) -> Sequence[AppCommand]:
        built_commands: dict[Unique, AppCommand] = {}

        for command in self._registry.values():
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
                    name=str_or_build_locale(unwrap(command.metadata.group).name)[0],
                    type=command.metadata.app_command.type,
                    guild_id=command.metadata.app_command.guild_id,
                    group=None,
                    sub_group=None,
                )

                if key not in built_commands:
                    built_commands[key] = AppCommand(
                        name=unwrap(command.metadata.group).name,
                        description=unwrap(command.metadata.group).description or "No Description",
                        type=command.metadata.app_command.type,
                        guild_id=command.metadata.app_command.guild_id,
                        options=[],
                        default_member_permissions=(
                            unwrap(command.metadata.group).default_member_permissions
                        ),
                        is_dm_enabled=unwrap(command.metadata.group).dm_enabled,
                    )

                # The top-level command now exists. A subcommand group now if placed
                # inside the top-level command. This subcommand group will hold `command`.

                children = cast("list[CommandOption]", unwrap(built_commands[key].options))

                name, name_localizations = str_or_build_locale(
                    unwrap(command.metadata.sub_group).name
                )
                description, description_localizations = str_or_build_locale(
                    unwrap(command.metadata.sub_group).description or "No Description"
                )

                sub_command_group = CommandOption(
                    name=name,
                    name_localizations=name_localizations,
                    description=description,
                    description_localizations=description_localizations,
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

                name, name_localizations = str_or_build_locale(command.metadata.app_command.name)
                assert command.metadata.app_command.description
                description, description_localizations = str_or_build_locale(
                    command.metadata.app_command.description
                )

                cast("list[CommandOption]", sub_command_group.options).append(
                    CommandOption(
                        name=name,
                        name_localizations=name_localizations,
                        description=description,
                        description_localizations=description_localizations,
                        type=OptionType.SUB_COMMAND,
                        options=command.metadata.app_command.options,
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
                    name=str_or_build_locale(command.metadata.group.name)[0],
                    type=command.metadata.app_command.type,
                    guild_id=command.metadata.app_command.guild_id,
                    group=None,
                    sub_group=None,
                )

                if key not in built_commands:
                    built_commands[key] = AppCommand(
                        name=command.metadata.group.name,
                        description=unwrap(command.metadata.group).description or "No Description",
                        type=command.metadata.app_command.type,
                        guild_id=command.metadata.app_command.guild_id,
                        options=[],
                        default_member_permissions=(
                            command.metadata.group.default_member_permissions
                        ),
                        is_dm_enabled=command.metadata.group.dm_enabled,
                    )

                # No checking has to be done before appending `command` since it is the
                # lowest level.
                name, name_localizations = str_or_build_locale(command.metadata.app_command.name)
                assert command.metadata.app_command.description
                description, description_localizations = str_or_build_locale(
                    command.metadata.app_command.description
                )

                cast("list[CommandOption]", built_commands[key].options).append(
                    CommandOption(
                        name=name,
                        name_localizations=name_localizations,
                        description=description,
                        description_localizations=description_localizations,
                        type=command.metadata.app_command.type,
                        options=command.metadata.app_command.options,
                        is_required=False,
                    )
                )

            else:
                built_commands[Unique.from_meta_struct(command)] = command.metadata.app_command

        return tuple(built_commands.values())

    async def __post_guild_commands(
        self, commands: Sequence[CanBuild], guild: Snowflakeish
    ) -> None:
        try:
            if self._application_id is None:
                raise AttributeError("Client `application_id` is not defined")
            await self._client.app.rest.set_application_commands(
                application=self._application_id,
                # The only method that is called has been implemented.
                commands=commands,  # type: ignore
                guild=guild,
            )
        except ForbiddenError:
            if not isinstance(self._client.app, CacheAware):
                return

            if guild in self._client.app.cache.get_guilds_view():
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

    async def purge_commands(
        self,
        *guilds: SnowflakeishOr[PartialGuild],
        skip_global: bool = False,
        purge_everything: bool = True,
    ) -> None:
        """Purge application commands for this Command Handler.

        Args:
            *guilds: The guilds to purge commands from, if any.

        Kwargs:
            skip_global:
                If `True`, skip purging global commands.
            purge_everything:
                If `True`, purge all global commands and commands in
                all `tracked_guilds`. This option takes priority over
                `skip_global`.
        """
        if self._application_id is None:
            raise AttributeError("Client `application_id` is not defined")

        if not skip_global or purge_everything:
            await self._client.app.rest.set_application_commands(self._application_id, ())

        guilds_to_purge: Iterable[PartialGuild | Snowflake | int]
        if purge_everything:
            guilds_to_purge = {*guilds, *self._guilds}
        else:
            guilds_to_purge = guilds

        for guild in guilds_to_purge:
            await self._client.app.rest.set_application_commands(self._application_id, (), guild)

    async def register_commands(self) -> None:
        guilds = list(self._guilds)

        commands = self.__build_commands()

        command_guilds: DefaultDict[Snowflakeish, list[AppCommand]] = defaultdict(list)
        global_commands: list[AppCommand] = []

        for command in commands:
            if command.guild_id:
                command_guilds[command.guild_id].append(command)
                if command.guild_id in guilds:
                    guilds.remove(command.guild_id)
            else:
                global_commands.append(command)

        if not self._application_id:
            me = await self._client.app.rest.fetch_application()
            self._application_id = me.id

        await gather(
            self._client.app.rest.set_application_commands(
                application=self._application_id,
                # The only method that is called has been implemented.
                commands=global_commands,  # type: ignore
            ),
            gather_iter(
                self.__post_guild_commands(commands, guild)
                for guild, commands in command_guilds.items()
            ),
            gather_iter(
                self._client.app.rest.set_application_commands(
                    application=self._application_id, commands=[], guild=guild
                )
                for guild in guilds
            ),
        )

    @property
    def crescent_commands(self) -> Iterable[AppCommandMeta]:
        """
        Returns the information crescent stores for all the commands registered
        to the bot.
        """
        return (command.metadata for command in self._registry.values())

    @property
    def app_commands(self) -> Iterable[AppCommand]:
        """
        Returns the app commands registered to this bot.
        """
        return (command.metadata.app_command for command in self._registry.values())
