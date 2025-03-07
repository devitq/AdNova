from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_dialog import DialogManager

logout_router = Router()


@logout_router.message(Command("logout"))
async def logout_command(
    message: Message, dialog_manager: DialogManager, state: FSMContext
) -> None:
    state_data = await state.get_data()

    if state_data["authenticated"]:
        await dialog_manager.reset_stack()
        del state_data["advertiser_id"]
        await state.set_data(state_data)
        await message.answer("Successfully logged out.")
