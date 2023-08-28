from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.filters.user import ProductMenuFilter
from src.bot.structures.role import Role
from src.db.models import User, Category


async def create_main_user_kb(user: User) -> ReplyKeyboardMarkup:
    start_kb = [
        [KeyboardButton(text='Каталог'), KeyboardButton(text='Корзина')],
        [KeyboardButton(text='Помощь'), KeyboardButton(text='Поддержка')],
    ]
    if user.role == Role.ADMINISTRATOR or user.role == Role.MODERATOR:
        start_kb.append([KeyboardButton(text='Админ-панель')])
    elif user.request_status_moder == 0:
        start_kb.append([KeyboardButton(text='Получить модератора 🙇')])
    return ReplyKeyboardMarkup(
        keyboard=start_kb,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Выберите один из вариантов👇',
    )


async def create_product_kb(product_name: str) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardBuilder()
    ikb.button(text='Добавить в корзину ✅', callback_data=ProductMenuFilter(product_name=product_name))

    return ikb.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
    )
