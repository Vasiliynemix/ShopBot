from aiogram.fsm.state import StatesGroup, State


class AddProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    category = State()
    result = State()


class AddCategory(StatesGroup):
    new_category = State()
