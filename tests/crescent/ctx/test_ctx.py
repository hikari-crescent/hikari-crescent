from pytest import mark

from crescent.context import BaseContext, support_custom_context


def test_into():
    ctx = BaseContext(
        interaction=1,
        client=2,
        app=3,
        application_id=4,
        type=5,
        token=6,
        id=7,
        version=8,
        channel_id=9,
        guild_id=10,
        user=11,
        member=12,
        locale=13,
        command=14,
        command_type=15,
        group=16,
        sub_group=17,
        options=18,
        _has_created_message=19,
        _has_deferred_response=20,
        _rest_interaction_future=21,
    )

    ctx2 = ctx.into(BaseContext)

    assert ctx.interaction == ctx2.interaction
    assert ctx.app == ctx2.app
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
    assert ctx.locale == ctx2.locale
    assert ctx.command == ctx2.command
    assert ctx.command_type == ctx2.command_type
    assert ctx.group == ctx2.group
    assert ctx.sub_group == ctx2.sub_group
    assert ctx.options == ctx2.options
    assert ctx._has_created_message == ctx2._has_created_message
    assert ctx._has_deferred_response == ctx2._has_deferred_response
    assert ctx._rest_interaction_future == ctx2._rest_interaction_future


@mark.asyncio
async def test_supports_context():
    class CustomContext(BaseContext):
        ...

    async def callback(ctx: CustomContext, arg, kwarg=None):
        assert type(ctx) is CustomContext
        assert arg == 5
        assert kwarg == 10

    ctx = BaseContext(
        interaction=None,
        app=None,
        client=None,
        application_id=None,
        type=None,
        token=None,
        id=None,
        version=None,
        channel_id=None,
        guild_id=None,
        user=None,
        member=None,
        locale=None,
        command=None,
        command_type=None,
        group=None,
        sub_group=None,
        options=None,
        _has_created_message=None,
        _has_deferred_response=None,
        _rest_interaction_future=None,
    )

    await support_custom_context(callback)(ctx, 5, kwarg=10)
