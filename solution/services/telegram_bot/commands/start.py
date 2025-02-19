from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from states.start import StartDialogState

start_router = Router()


@start_router.message(CommandStart())
async def start_command(
    message: Message, dialog_manager: DialogManager, state: FSMContext
) -> None:
    state_data = await state.get_data()

    if state_data["authenticated"]:
        await message.answer(
            "Already authenticated as"
            f" <code>{state_data['advertiser']['name']}</code>"
        )
        return

    await dialog_manager.start(
        state=StartDialogState.start, mode=StartMode.RESET_STACK
    )
