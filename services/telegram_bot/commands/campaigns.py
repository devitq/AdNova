from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from filters.auth import AuthenticatedFilter
from states.campaigns import CampaignsDailogState

campaigns_router = Router()


@campaigns_router.message(Command("campaigns"), AuthenticatedFilter())
async def stats_command(
    message: Message, dialog_manager: DialogManager, state: FSMContext
) -> None:
    await dialog_manager.start(
        state=CampaignsDailogState.campaigns, mode=StartMode.RESET_STACK
    )
