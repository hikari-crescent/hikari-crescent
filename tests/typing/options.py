from __future__ import annotations

from typing import Literal, assert_type

from hikari import Attachment, InteractionChannel, Role, User

from crescent import Context, Mentionable, options


class SimpleCases:
    str = options.String("Text option")
    int = options.Integer("Integer option")
    float = options.Float("Float option")
    bool = options.Boolean("Boolean option")
    channel = options.Channel("Channel option")
    role = options.Role("Role option")
    user = options.User("User option")
    mentionable = options.Mentionable("Mentionable option")
    attachment = options.Attachment("Attachment option.")

    def callback(self, ctx: Context) -> None:
        assert_type(self.str, str)
        assert_type(self.int, int)
        assert_type(self.float, float)
        assert_type(self.bool, bool)
        assert_type(self.channel, InteractionChannel)
        assert_type(self.role, Role)
        assert_type(self.user, User)
        assert_type(self.mentionable, Mentionable)
        assert_type(self.attachment, Attachment)


def yessman(_arg: object) -> Literal[True]:
    return True


class ComplexCases:
    yesman = options.Boolean("Yessman option", converter=yessman)
    default = options.Integer("int", default=None)

    def callback(self, ctx: Context) -> None:
        assert_type(self.yesman, Literal[True])
        assert_type(self.default, int | None)
