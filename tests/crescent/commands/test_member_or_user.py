import logging
from contextlib import suppress

import hikari
from pytest import LogCaptureFixture, raises

import crescent


def test_log_warning_when_user_dm_disabled(caplog: LogCaptureFixture):
    with caplog.at_level(logging.WARN):

        @crescent.command(dm_enabled=False)
        async def _(ctx: crescent.Context, user: hikari.User):
            ...

    assert caplog.text


def test_no_log_when_user_dm_enabled(caplog: LogCaptureFixture):
    with caplog.at_level(logging.WARN):

        @crescent.command(dm_enabled=True)
        async def _(ctx: crescent.Context, user: hikari.User):
            ...

    assert not caplog.text


def test_exception_when_member_dm_enabled():
    with raises(TypeError):

        @crescent.command(dm_enabled=True)
        async def _(ctx: crescent.Context, user: hikari.Member):
            ...


def test_no_log_when_member_dm_enabled(caplog: LogCaptureFixture):
    with caplog.at_level(logging.WARN):
        with suppress(TypeError):

            @crescent.command(dm_enabled=True)
            async def _(ctx: crescent.Context, user: hikari.Member):
                ...

    assert not caplog.text


def test_no_log_when_member_dm_disabled(caplog: LogCaptureFixture):
    with caplog.at_level(logging.WARN):

        @crescent.command(dm_enabled=False)
        async def _(ctx: crescent.Context, user: hikari.Member):
            ...

    assert not caplog.text
