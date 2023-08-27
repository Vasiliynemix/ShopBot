from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.structures.role import Role
from src.db.models import User, Category


async def create_main_user_kb(user: User) -> ReplyKeyboardMarkup:
    start_kb = [
        [KeyboardButton(text='Каталог'), KeyboardButton(text='Корзина')],
        [KeyboardButton(text='Помощь'), KeyboardButton(text='Поддержка')],
    ]
    if user.role == Role.ADMINISTRATOR or user.role == Role.MODERATOR:
        start_kb.append([KeyboardButton(text='Админ-панель')])
    else:
        start_kb.append([KeyboardButton(text='Получить модератора 🙇')])
    return ReplyKeyboardMarkup(
        keyboard=start_kb,
        resize_keyboard=True,
        input_field_placeholder='Выберите один из вариантов👇',
    )
