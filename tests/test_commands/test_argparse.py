from inspect import _empty

from hikari import (
    ChannelType,
    CommandChoice,
    CommandOption,
    DMChannel,
    GroupDMChannel,
    GuildCategory,
    GuildChannel,
    GuildNewsChannel,
    GuildStageChannel,
    GuildStoreChannel,
    GuildTextChannel,
    GuildVoiceChannel,
    OptionType,
    PartialChannel,
    PrivateChannel,
    TextableChannel,
    TextableGuildChannel,
)
from typing_extensions import Annotated

from crescent import Name, Choices, ChannelTypes, MaxValue, MinValue, Description
from crescent.commands.decorators import _gen_command_option, _Parameter


def test_gen_command_option():
    assert _gen_command_option(
        _Parameter(
            name="self",
            annotation=_empty,
            empty=_empty,
            default=None,
        )
    ) is None

    assert _gen_command_option(
        _Parameter(
            name="1234",
            annotation=str,
            empty=_empty,
            default=_empty,
        )
    ) == CommandOption(
        name="1234",
        type=OptionType.STRING,
        description="No Description",
        is_required=True,
    )

    assert _gen_command_option(
        _Parameter(
            name="1234",
            annotation=str,
            empty=_empty,
            default=12345,
        )
    ) == CommandOption(
        name="1234",
        type=OptionType.STRING,
        description="No Description",
        is_required=False,
    )


def test_annotations():
    annotations = (
        (Annotated[str, "1234"], {"type": OptionType.STRING, "description": "1234"}),
        (Annotated[str, Description("1234")], {"type": OptionType.STRING, "description": "1234"}),
        (Annotated[str, Name("different_name")], {
         "type": OptionType.STRING, "name": "different_name"
         }),
        (Annotated[int, MinValue(10), MaxValue(15)], {
            "type": OptionType.INTEGER, "min_value": 10, "max_value": 15
        }),
        (Annotated[PartialChannel, ChannelTypes(ChannelType.GUILD_NEWS)], {
            "type": OptionType.CHANNEL, "channel_types": [ChannelType.GUILD_NEWS]
        }),
        (Annotated[str, Choices(
            CommandChoice(name="option1", value=15),
            CommandChoice(name="option2", value=30),
        )], {
            "type": OptionType.STRING,
            "choices": (
                CommandChoice(name="option1", value=15),
                CommandChoice(name="option2", value=30),
            )
        }),
    )

    for annotation, params in annotations:
        kwargs = {
            "name": "1234",
            "description": "No Description",
        }
        kwargs.update(params)

        assert _gen_command_option(
            _Parameter(
                name="1234",
                annotation=annotation,
                empty=_empty,
                default=None,
            )
        ) == CommandOption(
            **kwargs,
        )


def test_gen_channel_options():
    channels = (
        (PartialChannel, None),
        (PrivateChannel, [ChannelType.DM, ChannelType.GROUP_DM]),
        (DMChannel, [ChannelType.DM]),
        (GroupDMChannel, [ChannelType.GROUP_DM]),
        (TextableChannel, [ChannelType.GUILD_TEXT, ChannelType.DM, ChannelType.GUILD_NEWS]),
        (GuildCategory, [ChannelType.GUILD_CATEGORY]),
        (TextableGuildChannel, [ChannelType.GUILD_TEXT, ChannelType.GUILD_NEWS]),
        (GuildTextChannel, [ChannelType.GUILD_TEXT]),
        (GuildNewsChannel, [ChannelType.GUILD_NEWS]),
        (GuildStoreChannel, [ChannelType.GUILD_STORE]),
        (GuildVoiceChannel, [ChannelType.GUILD_VOICE]),
        (GuildStageChannel, [ChannelType.GUILD_STAGE]),
        (GuildChannel, [
            ChannelType.GUILD_TEXT,
            ChannelType.GUILD_VOICE,
            ChannelType.GUILD_CATEGORY,
            ChannelType.GUILD_NEWS,
            ChannelType.GUILD_STORE,
            ChannelType.GUILD_STAGE,
        ]),
    )

    for channel_in, channel_types in channels:
        assert _gen_command_option(
            _Parameter(
                name="1234",
                annotation=channel_in,
                empty=_empty,
                default=12345,
            )
        ) == CommandOption(
            name="1234",
            type=OptionType.CHANNEL,
            description="No Description",
            is_required=False,
            channel_types=channel_types
        )
