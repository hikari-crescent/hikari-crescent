from hikari import AutocompleteInteractionOption, OptionType
from pytest import mark

from crescent.internal.handle_resp import _get_option_recursive


@mark.asyncio
class TestAutocompleteResp:
    async def test_top_level_command(self):

        options = [
            AutocompleteInteractionOption(
                name="option_1", type=OptionType.STRING, value=None, is_focused=False, options=[]
            ),
            AutocompleteInteractionOption(
                name="option_2", type=OptionType.STRING, value=None, is_focused=True, options=[]
            ),
            AutocompleteInteractionOption(
                name="option_3", type=OptionType.STRING, value=None, is_focused=False, options=[]
            ),
        ]

        assert _get_option_recursive(options).name == "option_2"

    async def test_group(self):
        options = [
            AutocompleteInteractionOption(
                name="option_1", type=OptionType.STRING, value=None, is_focused=False, options=[]
            ),
            AutocompleteInteractionOption(
                name="option_2",
                type=OptionType.STRING,
                value=None,
                is_focused=False,
                options=[
                    AutocompleteInteractionOption(
                        name="option_4",
                        type=OptionType.STRING,
                        value=None,
                        is_focused=False,
                        options=[],
                    ),
                    AutocompleteInteractionOption(
                        name="option_5",
                        type=OptionType.STRING,
                        value=None,
                        is_focused=True,
                        options=[],
                    ),
                ],
            ),
            AutocompleteInteractionOption(
                name="option_3", type=OptionType.STRING, value=None, is_focused=False, options=[]
            ),
        ]

        assert _get_option_recursive(options).name == "option_5"

    async def test_sub_group(self):
        options = [
            AutocompleteInteractionOption(
                name="option_1", type=OptionType.STRING, value=None, is_focused=False, options=[]
            ),
            AutocompleteInteractionOption(
                name="option_2",
                type=OptionType.STRING,
                value=None,
                is_focused=False,
                options=[
                    AutocompleteInteractionOption(
                        name="option_4",
                        type=OptionType.STRING,
                        value=None,
                        is_focused=False,
                        options=[],
                    ),
                    AutocompleteInteractionOption(
                        name="option_5",
                        type=OptionType.STRING,
                        value=None,
                        is_focused=False,
                        options=[
                            AutocompleteInteractionOption(
                                name="option_6",
                                type=OptionType.STRING,
                                value=None,
                                is_focused=True,
                                options=[],
                            ),
                            AutocompleteInteractionOption(
                                name="option_7",
                                type=OptionType.STRING,
                                value=None,
                                is_focused=False,
                                options=[],
                            ),
                        ],
                    ),
                ],
            ),
            AutocompleteInteractionOption(
                name="option_3", type=OptionType.STRING, value=None, is_focused=False, options=[]
            ),
        ]

        assert _get_option_recursive(options).name == "option_6"
