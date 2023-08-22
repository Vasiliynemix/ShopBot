from aiogram.fsm.state import State, StatesGroup


class AdminFSM(StatesGroup):
    add_admin = State()
