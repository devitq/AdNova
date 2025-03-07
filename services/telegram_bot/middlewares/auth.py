from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from api.client import AdNovaClient
from api.errors import HTTPError


class AuthMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        state: FSMContext = data["state"]
        state_data = await state.get_data()

        if "advertiser_id" in state_data:
            advertiser_id = state_data["advertiser_id"]
            async with AdNovaClient() as client:
                try:
                    advertiser = await client.get_advertiser(advertiser_id)
                    state_data["authenticated"] = True
                    state_data["advertiser"] = advertiser.model_dump(
                        mode="json"
                    )
                except HTTPError:
                    state_data["authenticated"] = False
                    state_data["advertiser_id"] = None
        else:
            state_data["authenticated"] = False
            state_data["advertiser_id"] = None

        await state.set_data(state_data)

        return await handler(event, data)
