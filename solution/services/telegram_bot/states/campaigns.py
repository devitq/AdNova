from aiogram.fsm.state import State, StatesGroup


class CampaignsDailogState(StatesGroup):
    campaigns = State()
    campaign = State()
    campaign_upload_ad_image = State()
    campaign_create = State()
    campaign_edit = State()
