from hikari import (
    Attachment,
    GuildTextChannel,
    GuildVoiceChannel,
    Member,
    OptionType,
    PartialChannel,
    Role,
    User,
)

from crescent import Mentionable, command, option


def test_option_types():
    @command(name="all-option-types")
    class AllOptionTypes:
        text = option(str)
        integer = option(int)
        boolean = option(bool)
        number = option(float)
        user = option(User)
        role = option(Role)
        mentionable = option(Mentionable)
        channel = option(PartialChannel)
        channel_list = option([GuildTextChannel, GuildVoiceChannel])
        attachment = option(Attachment)

    options = AllOptionTypes.metadata.app.options

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


def test_member():
    @command(name="member-type", dm_enabled=False)
    class MemberType:
        member = option(Member)

    assert MemberType.metadata.app.options[0].type == OptionType.USER
