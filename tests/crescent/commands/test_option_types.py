from hikari import ChannelType, OptionType

from crescent import command, opt


def test_option_types():
    @command(name="all-option-types")
    class AllOptionTypes:
        text = opt.string("text")
        integer = opt.number("integer")
        boolean = opt.boolean("boolean")
        number = opt.floating("number")
        user = opt.user("user")
        role = opt.role("role")
        mentionable = opt.mentionable("mentionable")
        channel = opt.channel("channel")
        channel_list = opt.channel("channel list").channel_types(
            [ChannelType.GUILD_TEXT, ChannelType.GUILD_VOICE]
        )
        attachment = opt.attachment("attachment")

        async def callback(self, ctx): ...

    options = AllOptionTypes.metadata.app_command.options

    assert options

    assert options[0].type == OptionType.STRING
    assert options[1].type == OptionType.INTEGER
    assert options[2].type == OptionType.BOOLEAN
    assert options[3].type == OptionType.FLOAT
    assert options[4].type == OptionType.USER
    assert options[5].type == OptionType.ROLE
    assert options[6].type == OptionType.MENTIONABLE
    assert options[7].type == OptionType.CHANNEL
    assert options[8].type == OptionType.CHANNEL
    assert options[9].type == OptionType.ATTACHMENT


def test_string_length_limits():
    @command(name="string-length-limits")
    class StringLengthLimits:
        value = opt.string("value").min_length(2).max_length(4)

        async def callback(self, ctx): ...

    options = StringLengthLimits.metadata.app_command.options

    assert options
    assert options[0].min_length == 2
    assert options[0].max_length == 4
    assert options[0].min_value is None
    assert options[0].max_value is None
