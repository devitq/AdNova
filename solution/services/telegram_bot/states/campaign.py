from aiogram.fsm.state import State, StatesGroup


class CampaignDialogState(StatesGroup):
    ad_title = State()
    ad_text = State()
    impressions_limit = State()
    clicks_limit = State()
    cost_per_impression = State()
    cost_per_click = State()
    start_date = State()
    end_date = State()
    gender = State()
    age_from = State()
    age_to = State()
    location = State()
    delete_ad_image = State()
