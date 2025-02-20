from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_dialog import DialogManager

from api.client import AdNovaClient
from filters.auth import AuthenticatedFilter

statistics_router = Router()


@statistics_router.message(Command("statistics"), AuthenticatedFilter())
async def stats_command(
    message: Message, dialog_manager: DialogManager, state: FSMContext
) -> None:
    state_data = await state.get_data()
    advertiser_id = state_data["advertiser_id"]

    async with AdNovaClient() as client:
        stats = await client.get_advertiser_statistics(advertiser_id)

    response = (
        f"📊 Overall <code>{state_data['advertiser']['name']}</code>"
        " statistics:\n\n"
        f"\t• Impressions: {stats.impressions_count}\n"
        f"\t• Clicks: {stats.clicks_count}\n"
        f"\t• Conversion: {stats.conversion:.2f}%\n"
        f"\t• Spent on impressions: ${stats.spent_impressions:.2f}\n"
        f"\t• Spent on clicks: ${stats.spent_clicks:.2f}\n"
        f"\t• Spent total: ${stats.spent_total:.2f}"
    )
    await message.answer(response)
