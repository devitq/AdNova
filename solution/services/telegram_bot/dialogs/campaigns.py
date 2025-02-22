import tempfile
from http import HTTPStatus as status
from mimetypes import guess_extension
from typing import Any
from urllib.parse import urlparse

import httpx
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ContentType, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.common import Whenable
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import Button, ListGroup, ScrollingGroup, Start
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format
from pydantic import ValidationError

import config
from api.client import AdNovaClient
from api.errors import BadRequestError, ForbiddenError
from dialogs import utils
from states.campaigns import CampaignsDailogState

campaign_info = (
    Const('<pre><code class="language-input-format">Title\n'),
    Const("Text\n"),
    Const("Impressions limit\n"),
    Const("Clicks limit\n"),
    Const("Cost per impression\n"),
    Const("Cost per click\n"),
    Const("Start date\n"),
    Const("End date\n"),
    Const("Targeting gender (ALL, FEMALE, MALE, None)\n"),
    Const("Targeting age from (could be None)\n"),
    Const("Targeting age to (could be None)\n"),
    Const("Targeting location (could be None)"),
    Const("</code></pre>"),
    Const('<pre><code class="language-example">Some title\n'),
    Const("Some text\n"),
    Const("15\n"),
    Const("10\n"),
    Const("0.4\n"),
    Const("0.5\n"),
    Const("100\n"),
    Const("110\n"),
    Const("ALL\n"),
    Const("12\n"),
    Const("None\n"),
    Const("Moscow"),
    Const("</code></pre>"),
)


def campaign_has_ad_image(
    data: dict, widget: Whenable, manager: DialogManager
) -> bool:
    return bool(data["dialog_data"]["campaign"]["ad_image"])


def campaign_has_not_ad_image(
    data: dict, widget: Whenable, manager: DialogManager
) -> bool:
    return not data["dialog_data"]["campaign"]["ad_image"]


def check_campaign(campaign_data: str) -> None:
    fields = campaign_data.split("\n\n")

    if len(fields) != 12:
        raise ValueError

    utils.campaign_from_list(fields)


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


async def campaign_on_error(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    error: object,
) -> None:
    if isinstance(error, ValidationError):
        await message.answer(f"Invalid campaign data: {error.json()}")
    elif isinstance(error, ValueError):
        await message.answer(f"Invalid campaign data {error!s}")


async def campaign_create_on_success(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    campaign_data: str,
) -> None:
    state = dialog_manager.middleware_data["state"]
    state_data = await state.get_data()

    fields = message.text.split("\n\n")

    campaign = utils.campaign_from_list(fields)

    async with AdNovaClient() as client:
        try:
            await client.create_campaign(
                advertiser_id=state_data["advertiser_id"], data=campaign
            )
            await dialog_manager.switch_to(CampaignsDailogState.campaigns)
        except BadRequestError as e:
            await message.answer(
                f"Invalid data: {e.model_dump(mode='json')['detail']}"
            )


async def campaign_edit_on_success(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    campaign_data: str,
) -> None:
    fields = message.text.split("\n\n")

    new_campaign = utils.campaign_from_list(fields)

    state = dialog_manager.middleware_data["state"]
    state_data = await state.get_data()

    manager_data: dict[Any] = await dialog_manager.load_data()

    campaign_id = manager_data["dialog_data"]["campaign"]["campaign_id"]

    async with AdNovaClient() as client:
        try:
            new_campaign = await client.update_campaign(
                advertiser_id=state_data["advertiser_id"],
                campaign_id=campaign_id,
                data=new_campaign,
            )
            await dialog_manager.update(
                {
                    "campaign": new_campaign.model_dump(mode="json"),
                }
            )
            await dialog_manager.switch_to(CampaignsDailogState.campaign)
        except BadRequestError as e:
            await message.answer(
                f"Invalid data: {e.model_dump(mode='json')['detail']}"
            )
        except ForbiddenError as e:
            await message.answer(
                "Forbidden changing campaign: "
                f"{e.model_dump(mode='json')['detail']}"
            )


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
        campaign_statistics = await client.get_campaign_statistics(
            campaign_id=campaign_id
        )

    if campaign.ad_image:
        campaign.ad_image = (
            f"{config.MINIO_URL}{urlparse(campaign.ad_image).path}"
        )

    await manager.update(
        {
            "campaign": campaign.model_dump(mode="json"),
            "campaign_statistics": campaign_statistics.model_dump(mode="json"),
        }
    )
    await callback.answer()
    await manager.switch_to(CampaignsDailogState.campaign)


async def campaign_edit_on_click(
    callback: CallbackQuery, button: Button, manager: DialogManager
) -> None:
    manager_data: dict[Any] = await manager.load_data()
    state: FSMContext = manager_data["middleware_data"]["state"]
    state_data = await state.get_data()

    advertiser_id = state_data["advertiser_id"]
    campaign_id = manager_data["dialog_data"]["campaign"]["campaign_id"]

    async with AdNovaClient() as client:
        campaign = await client.get_campaign(
            advertiser_id=advertiser_id,
            campaign_id=campaign_id,
        )

    await manager.update(
        {
            "campaign": campaign.model_dump(mode="json"),
        }
    )
    await callback.answer()
    await manager.switch_to(CampaignsDailogState.campaign_edit)


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


async def back_to_campaign(
    callback: CallbackQuery, button: Button, manager: DialogManager
) -> None:
    manager_data = await manager.load_data()
    state: FSMContext = manager_data["middleware_data"]["state"]
    state_data = await state.get_data()

    campaign = manager_data["dialog_data"]["campaign"]
    campaign_id = campaign["campaign_id"]
    advertiser_id = state_data["advertiser_id"]

    async with AdNovaClient() as client:
        campaign = await client.get_campaign(
            advertiser_id=advertiser_id,
            campaign_id=campaign_id,
        )

    await manager.update(
        {
            "campaign": campaign.model_dump(mode="json"),
        }
    )
    await callback.answer()
    await manager.switch_to(CampaignsDailogState.campaign)


campaigns_dialog = Dialog(
    Window(
        Const("Campaigns:"),
        Start(
            Const("➕ Create"),
            id="create_campaign",
            state=CampaignsDailogState.campaign_create,
        ),
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
        Const(
            "Enter campaign info in following format "
            "(each statement on new line with one enter between each):"
        ),
        *campaign_info,
        Start(
            Const("⬅️ Back to list"),
            id="back",
            state=CampaignsDailogState.campaigns,
        ),
        TextInput(
            id="campaign",
            type_factory=check_campaign,
            on_success=campaign_create_on_success,
            on_error=campaign_on_error,
        ),
        state=CampaignsDailogState.campaign_create,
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
        Const("\n📊 Statistics:\n"),
        Format(
            "Impressions: "
            "{dialog_data[campaign_statistics][impressions_count]}"
        ),
        Format("Clicks: {dialog_data[campaign_statistics][clicks_count]}"),
        Format(
            "Conversion: "
            "{dialog_data[campaign_statistics][impressions_count]:.2f}%"
        ),
        Format(
            "Spent on impressions: "
            "{dialog_data[campaign_statistics][impressions_count]:.2f}"
        ),
        Format(
            "Spent on clicks: "
            "{dialog_data[campaign_statistics][spent_clicks]:.2f}"
        ),
        Format(
            "Spent total: {dialog_data[campaign_statistics][spent_total]:.2f}"
        ),
        Button(
            Const("📝 Edit campaign"),
            id="edit_campaign",
            on_click=campaign_edit_on_click,
        ),
        Start(
            Const("⬆️ Upload image"),
            id="upload_ad_image",
            state=CampaignsDailogState.campaign_upload_ad_image,
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
        Start(
            Const("⬅️ Back to list"),
            id="back",
            state=CampaignsDailogState.campaigns,
        ),
        state=CampaignsDailogState.campaign,
        getter=campaign_by_id,
    ),
    Window(
        Const(
            "Enter new campaign info in following format "
            "(each statement on new line with one enter between each):"
        ),
        *campaign_info,
        Button(
            Const("⬅️ Back to campaign"),
            id="back_to_campaign",
            on_click=back_to_campaign,
        ),
        TextInput(
            id="campaign_update",
            type_factory=check_campaign,
            on_success=campaign_edit_on_success,
            on_error=campaign_on_error,
        ),
        state=CampaignsDailogState.campaign_edit,
    ),
)
