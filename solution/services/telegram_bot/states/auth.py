from aiogram.fsm.state import State, StatesGroup


class AuthState(StatesGroup):
    advertiser_id = State()
