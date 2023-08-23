from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.filters.admin import CallBackAdminListFilter, CallBackCategoriesListFilter
from src.db.models import User, Category


async def create_main_kb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardBuilder()
    ikb.row(InlineKeyboardButton(
        text='test',
        callback_data='test'
    ))
    return ikb.as_markup()


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


async def get_categories_ikb(categories: list[Category] | None):
    ikb = InlineKeyboardBuilder()
    if categories is not None:
        for category in categories:
            ikb.button(
                text=category.category_name,
                callback_data=CallBackCategoriesListFilter(category_name=category.category_name)
            )
    ikb.button(text='Добавить нужную категорию ✅', callback_data='add_category')
    ikb.adjust(1)

    return ikb.as_markup(resize_keyboard=True)


async def add_product_in_db() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardBuilder()
    ikb.button(text='Опубликовать ✅', callback_data='product_publish')
    ikb.button(text='Изменить какой-то пункт ⬅️', callback_data='product_update')
    ikb.button(text='Отменить публикацию ❌', callback_data='product_cancel')
    ikb.adjust(1)

    return ikb.as_markup(resize_keyboard=True)
