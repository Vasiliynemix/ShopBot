from aiogram.fsm.state import StatesGroup, State


class UserFSM(StatesGroup):
    catalog = State()


class CatalogFSM(StatesGroup):
    category = State()
