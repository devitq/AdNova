from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


class AuthenticatedFilter(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        message: Message,
        state: FSMContext,
    ) -> bool:
        state_data = await state.get_data()

        return bool(state_data.get("authenticated"))
