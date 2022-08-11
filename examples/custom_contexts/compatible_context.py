# type: ignore

import hikari
import crescent

# To maintain compatibility with `crescent.Context`, certain variables must be set in certain places.


class CustomContext(crescent.BaseContext):
    async def defer(self) -> None:
        # When creating a reponse with type `hikari.ResponseType.DEFERRED_MESSAGE_UPDATE`
        self._has_deferred_response = True
        self.app.rest.create_interaction_response(
            response_type=hikari.ResponseType.DEFERRED_MESSAGE_CREATE
        )

    async def create_response(self) -> None:
        # When creating a reponse with type `hikari.ResponseType.MESSAGE_CREATE``
        self._has_created_message = True
        self.app.rest.create_interaction_response(response_type=hikari.ResponseType.MESSAGE_CREATE)

    async def edit_response(self) -> None:
        # Set `self._has_created_message` to True when editing the response to a
        # deferred intereaction.
        self._has_created_message = True
        self.app.rest.edit_interaction_response(...)
