from aiogram.fsm.state import StatesGroup, State


class Moderator(StatesGroup):
    start = State()


class AddProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    category = State()
    image = State()
    result = State()


class UpdateProduct(StatesGroup):
    update = State()


class AddCategory(StatesGroup):
    new_category = State()
