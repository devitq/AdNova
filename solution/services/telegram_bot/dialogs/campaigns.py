import tempfile
from http import HTTPStatus as status
from mimetypes import guess_extension
from typing import Any
from urllib.parse import urlparse

import httpx
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ContentType
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.common import Whenable
from aiogram_dialog.widgets.kbd import Button, ListGroup, ScrollingGroup, Start
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format

import config
from api.client import AdNovaClient
from states.campaigns import CampaignsDailogState


async def campaigns(**kwargs: dict[Any]) -> dict[str, Any]:
    state: FSMContext = kwargs["state"]
    state_data = await state.get_data()

    async with AdNovaClient() as client:
        campaigns = await client.list_campaigns(state_data["advertiser_id"])

    campaigns = (
        [campaign.model_dump(mode="json") for campaign in campaigns]
        if campaigns != []
        else [{"campaign_id": "‎"}]
    )

    return {
        "campaigns": campaigns,
    }


async def campaign_detail_on_click(
    callback: CallbackQuery, button: Button, manager: DialogManager
) -> None:
    manager_data: dict[Any] = await manager.load_data()
    state: FSMContext = manager_data["middleware_data"]["state"]
    state_data = await state.get_data()

    advertiser_id = state_data["advertiser_id"]
    campaign_id = manager.item_id

    if campaign_id == "‎":
        return

    async with AdNovaClient() as client:
        campaign = await client.get_campaign(
            advertiser_id=advertiser_id,
            campaign_id=campaign_id,
        )

    if campaign.ad_image:
        campaign.ad_image = (
            f"{config.MINIO_URL}{urlparse(campaign.ad_image).path}"
        )

    await manager.update({"campaign": campaign.model_dump(mode="json")})
    await callback.answer()
    await manager.switch_to(CampaignsDailogState.campaign)


def campaign_has_ad_image(
    data: dict, widget: Whenable, manager: DialogManager
) -> bool:
    return bool(data["dialog_data"]["campaign"]["ad_image"])


def campaign_has_not_ad_image(
    data: dict, widget: Whenable, manager: DialogManager
) -> bool:
    return not data["dialog_data"]["campaign"]["ad_image"]


async def campaign_by_id(**kwargs: dict[Any]) -> dict[str, Any]:
    manager: DialogManager = kwargs["dialog_manager"]
    manager_data = await manager.load_data()
    ad_image_url = manager_data["dialog_data"]["campaign"]["ad_image"]

    if not ad_image_url:
        return {}

    async with httpx.AsyncClient() as client:
        response = await client.get(ad_image_url)

        if response.status_code == status.OK:
            content_type = response.headers.get("Content-Type", "image/jpeg")
            ext = guess_extension(content_type) or ".jpg"

            with tempfile.NamedTemporaryFile(
                suffix=ext, delete=False
            ) as temp_file:
                temp_file.write(response.content)
                temp_file.flush()
                temp_file_path = temp_file.name

            attachment = MediaAttachment(
                type=ContentType.PHOTO, path=temp_file_path
            )
        else:
            attachment = None

    return {"ad_image": attachment}


async def delete_ad_image(
    callback: CallbackQuery, button: Button, manager: DialogManager
) -> None:
    manager_data = await manager.load_data()
    state: FSMContext = manager_data["middleware_data"]["state"]
    state_data = await state.get_data()

    campaign = manager_data["dialog_data"]["campaign"]
    campaign_id = campaign["campaign_id"]
    advertiser_id = state_data["advertiser_id"]

    async with AdNovaClient() as client:
        await client.delete_ad_image(
            advertiser_id=advertiser_id, campaign_id=campaign_id
        )

    campaign["ad_image"] = None

    await callback.answer("Campaign image deleted")


async def delete_campaign(
    callback: CallbackQuery, button: Button, manager: DialogManager
) -> None:
    manager_data = await manager.load_data()
    state: FSMContext = manager_data["middleware_data"]["state"]
    state_data = await state.get_data()

    campaign = manager_data["dialog_data"]["campaign"]
    campaign_id = campaign["campaign_id"]
    advertiser_id = state_data["advertiser_id"]

    async with AdNovaClient() as client:
        await client.delete_campaign(
            advertiser_id=advertiser_id, campaign_id=campaign_id
        )

    await callback.answer("Campaign deleted")
    await manager.switch_to(CampaignsDailogState.campaigns)


async def back_to_list(
    callback: CallbackQuery, button: Button, manager: DialogManager
) -> None:
    await manager.switch_to(CampaignsDailogState.campaigns)


campaigns_dialog = Dialog(
    Window(
        Const("Campaigns:"),
        Button(Const("➕ Create"), id="create_campaign"),
        ScrollingGroup(
            ListGroup(
                Button(
                    Format("{item[campaign_id]}"),
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
    Window(
        DynamicMedia("ad_image", when=campaign_has_ad_image),
        Format("• ID: <code>{dialog_data[campaign][campaign_id]}</code>"),
        Format("• Title: {dialog_data[campaign][ad_title]}"),
        Format("• Text: {dialog_data[campaign][ad_text]}"),
        Format(
            "• Impressions limit: {dialog_data[campaign][impressions_limit]}"
        ),
        Format("• Clicks limit: {dialog_data[campaign][clicks_limit]}"),
        Format(
            "• Cost per impression: "
            "{dialog_data[campaign][cost_per_impression]}"
        ),
        Format("• Cost per click: {dialog_data[campaign][cost_per_click]}"),
        Format("• Start date: {dialog_data[campaign][start_date]}"),
        Format("• End date: {dialog_data[campaign][end_date]}"),
        Format("• Targeting"),
        Format("\t • Gender: {dialog_data[campaign][targeting][gender]}"),
        Format("\t • Age from: {dialog_data[campaign][targeting][age_from]}"),
        Format("\t • Age to: {dialog_data[campaign][targeting][age_to]}"),
        Format("\t • Location: {dialog_data[campaign][targeting][location]}"),
        Button(Const("📝 Edit campaign"), id="edit_campaign"),
        Start(
            Const("⬆️ Upload image"),
            id="upload_ad_image",
            state=CampaignsDailogState.campaign_upload_ad_image,
            data=None,
            when=campaign_has_not_ad_image,
        ),
        Button(
            Const("🗑️ Delete image"),
            id="delete_image",
            on_click=delete_ad_image,
            when=campaign_has_ad_image,
        ),
        Button(
            Const("🗑️ Delete campaign"),
            id="delete_ad_image",
            on_click=delete_campaign,
        ),
        Button(Const("⬅️ Back to list"), id="back", on_click=back_to_list),
        state=CampaignsDailogState.campaign,
        getter=campaign_by_id,
    ),
)
