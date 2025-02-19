from aiogram.fsm.state import State, StatesGroup


class CampaignsDailogState(StatesGroup):
    campaigns = State()
    campaign = State()
