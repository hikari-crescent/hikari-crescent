from __future__ import annotations

from unittest.mock import Mock

import pytest
from hikari import AutocompleteInteraction, CommandInteraction, CommandType, Locale

from crescent.context import AutocompleteContext, Context
from crescent.internal.handle_resp import _context_from_interaction_resp


@pytest.mark.parametrize(
    ("interaction_type", "context_type"),
    [(CommandInteraction, Context), (AutocompleteInteraction, AutocompleteContext)],
)
def test_context_from_interaction(interaction_type, context_type):
    interaction = Mock(
        spec=interaction_type,
        command_name="test",
        command_type=CommandType.SLASH,
        locale=Locale.EN_US,
        options=[],
    )
    client = Mock()

    ctx = _context_from_interaction_resp(client, interaction)

    assert type(ctx) is context_type
    assert ctx.interaction is interaction
    assert ctx.client is client
    assert ctx.app is client.app
    assert ctx.command == "test"
    assert ctx.options == {}
    assert not ctx._has_created_response
    assert not ctx._has_deferred_response
    assert ctx._rest_interaction_future is None
