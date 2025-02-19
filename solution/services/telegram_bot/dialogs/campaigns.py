from typing import Any

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, ListGroup, ScrollingGroup
from aiogram_dialog.widgets.text import Const, Format

from api.client import AdNovaClient
from states.campaigns import CampaignsDailogState


async def campaigns(**kwargs: dict[Any]) -> dict[str, Any]:
    state: FSMContext = kwargs["state"]
    state_data = await state.get_data()

    async with AdNovaClient() as client:
        campaigns = await client.list_campaigns(state_data["advertiser_id"])

    campaigns = [campaign.model_dump(mode="json") for campaign in campaigns]

    return {
        "campaigns": campaigns,
    }


async def campaign_detail_on_click(
    callback: CallbackQuery, button: Button, manager: DialogManager
) -> None:
    await callback.answer()


campaigns_dialog = Dialog(
    Window(
        Const("Campaigns:"),
        ScrollingGroup(
            ListGroup(
                Button(
                    Format("{item[ad_title]}"),
                    id="detail",
                    on_click=campaign_detail_on_click,
                ),
                id="campaigns",
                item_id_getter=lambda item: item["campaign_id"],
                items="campaigns",
            ),
            id="pagination",
            width=1,
            height=4,
        ),
        state=CampaignsDailogState.campaigns,
        getter=campaigns,
    ),
)
