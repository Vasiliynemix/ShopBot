from aiogram.fsm.state import StatesGroup, State


class Moderator(StatesGroup):
    start = State()


class AddProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    category = State()
    image = State()
    test_publish = State()
    result = State()


class UpdateProduct(StatesGroup):
    update = State()
    update_one_value = State()
    update_image = State()
    new_category = State()


class AddCategory(StatesGroup):
    new_category = State()
