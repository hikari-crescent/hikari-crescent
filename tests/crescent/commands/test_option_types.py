from __future__ import annotations

from hikari import ChannelType, OptionType

from crescent import command, options


def test_option_types():
    @command(name="all-option-types")
    class AllOptionTypes:
        text = options.String("text", choices=[])
        integer = options.Integer("integer")
        boolean = options.Boolean("boolean")
        number = options.Float("number")
        user = options.User("user")
        role = options.Role("role")
        mentionable = options.Mentionable("mentionable")
        channel = options.Channel("channel", channel_types=[])
        channel_list = options.Channel(
            "channel list", channel_types=(ChannelType.GUILD_TEXT, ChannelType.GUILD_VOICE)
        )
        attachment = options.Attachment("attachment")

        async def callback(self, ctx): ...

    command_options = AllOptionTypes.metadata.app_command.options

    assert command_options

    assert command_options[0].type == OptionType.STRING
    assert command_options[1].type == OptionType.INTEGER
    assert command_options[2].type == OptionType.BOOLEAN
    assert command_options[3].type == OptionType.FLOAT
    assert command_options[4].type == OptionType.USER
    assert command_options[5].type == OptionType.ROLE
    assert command_options[6].type == OptionType.MENTIONABLE
    assert command_options[7].type == OptionType.CHANNEL
    assert command_options[8].type == OptionType.CHANNEL
    assert command_options[9].type == OptionType.ATTACHMENT
    assert command_options[8].channel_types == [ChannelType.GUILD_TEXT, ChannelType.GUILD_VOICE]
    assert command_options[0].choices is None
    assert command_options[7].channel_types is None


def test_string_length_limits():
    @command(name="string-length-limits")
    class StringLengthLimits:
        value = options.String("value", min_length=2, max_length=4)

        async def callback(self, ctx): ...

    command_options = StringLengthLimits.metadata.app_command.options

    assert command_options
    assert command_options[0].min_length == 2
    assert command_options[0].max_length == 4
    assert command_options[0].min_value is None
    assert command_options[0].max_value is None
