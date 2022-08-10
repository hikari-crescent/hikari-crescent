from crescent.context import BaseContext


def test_into():
    ctx = BaseContext(
        interaction=1,
        app=2,
        application_id=3,
        type=4,
        token=5,
        id=6,
        version=7,
        channel_id=8,
        guild_id=9,
        user=10,
        member=11,
        command=12,
        command_type=13,
        group=14,
        sub_group=15,
        options=16,
        has_created_message=17,
        has_deferred_response=18,
    )

    ctx2 = ctx.into(BaseContext)

    assert ctx.interaction == ctx2.interaction
    assert ctx.app == ctx2.app
    assert ctx.application_id == ctx2.application_id
    assert ctx.type == ctx2.type
    assert ctx.token == ctx2.token
    assert ctx.id == ctx2.id
    assert ctx.version == ctx2.version
    assert ctx.channel_id == ctx2.channel_id
    assert ctx.guild_id == ctx2.guild_id
    assert ctx.user == ctx2.user
    assert ctx.member == ctx2.member
    assert ctx.command == ctx2.command
    assert ctx.command_type == ctx2.command_type
    assert ctx.group == ctx2.group
    assert ctx.sub_group == ctx2.sub_group
    assert ctx.options == ctx2.options
    assert ctx._has_created_message == ctx2._has_created_message
    assert ctx._has_deferred_response == ctx2._has_deferred_response
