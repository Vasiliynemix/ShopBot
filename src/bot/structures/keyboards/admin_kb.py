from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.filters.admin import CallBackAdminListFilter
from src.db.models import User


def create_main_kb() -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(InlineKeyboardButton(
        text='test',
        callback_data='test'
    ))
    return kb_builder.as_markup()


async def get_moderators_ikb(moderators: list[User]):
    ikb = InlineKeyboardBuilder()
    for moderator in moderators:
        text = f'{moderator.user_id} | {moderator.user_name} | {moderator.role.name} ❌'
        ikb.button(
            text=text,
            callback_data=CallBackAdminListFilter(admin_id=moderator.user_id)
        )
    ikb.button(text='Добавить модератора ✅', callback_data='add_moderator')
    ikb.button(text='Вернуться в меню ⬅️', callback_data='start_menu')
    ikb.adjust(1)

    return ikb.as_markup(resize_keyboard=True)
