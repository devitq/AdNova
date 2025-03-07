from aiogram.fsm.state import State, StatesGroup


class StartDialogState(StatesGroup):
    start = State()
