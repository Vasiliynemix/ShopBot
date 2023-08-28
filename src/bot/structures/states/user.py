from aiogram.fsm.state import StatesGroup, State


class UserFSM(StatesGroup):
    catalog = State()
    product = State()
