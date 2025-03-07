from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_dialog import DialogManager

help_router = Router()


@help_router.message(Command("help"))
async def help_command(
    message: Message, dialog_manager: DialogManager, state: FSMContext
) -> None:
    response = (
        "Commands:\n\n"
        "/start - Start the bot and authenticate as advertiser\n"
        "/campaigns - Manage your campaigns\n"
        "/statistics - See your overall statistics\n"
        "/logout - Logout of current advertiser account"
    )
    await message.answer(response)
