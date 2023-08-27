from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.filters.admin import CallBackAdminListFilter, CallBackRequestStatusModeratorFilter
from src.bot.filters.user import CallBackCategoriesListFilter
from src.db.models import User, Category


async def start_admin_kb():
    ikb = InlineKeyboardBuilder()
    ikb.button(text='Добавить товар на продажу ✅', callback_data=f'add_product_in_db')
    ikb.adjust(1)

    return ikb.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
    )


async def get_moderators_ikb(moderators: list[User]) -> InlineKeyboardMarkup:
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


async def requests_add_status_moderator(user_id: int) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardBuilder()
    ikb.button(
        text='Принять заявку ✅',
        callback_data=CallBackRequestStatusModeratorFilter(user_id=f'accept_request{user_id}')
    )
    ikb.button(
        text='Отклонить заявку ✅',
        callback_data=CallBackRequestStatusModeratorFilter(user_id=f'reject_request{user_id}')
    )
    ikb.adjust(2)

    return ikb.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
    )


async def get_categories_ikb(
        categories: list[Category] | None,
        is_admin_mode: bool = False,
        is_update_mode: bool = False
) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardBuilder()
    if categories is not None:
        for category in categories:
            ikb.button(
                text=category.category_name,
                callback_data=CallBackCategoriesListFilter(category_name=category.category_name)
            )
    if is_admin_mode:
        ikb.button(text='Добавить нужную категорию ✅', callback_data=f'add_category')
    if is_update_mode:
        ikb.button(text=f'Назад ⬅️', callback_data='cancel_update_value')
    ikb.adjust(1)
    return ikb.as_markup(resize_keyboard=True)


async def add_product_in_db() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardBuilder()
    ikb.button(text='Опубликовать ✅', callback_data=f'product_publish')
    ikb.button(text='Изменить какой-то пункт ⬅️', callback_data=f'product_update')
    ikb.button(text='Отменить публикацию ❌', callback_data=f'product_cancel')
    ikb.adjust(1)

    return ikb.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
    )


async def save_images_in_static() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardBuilder()
    ikb.button(text='Продолжить ✅', callback_data='product_test_publish')
    ikb.adjust(1)

    return ikb.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
    )


async def create_update_kb(data: dict[str]) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardBuilder()
    ikb.button(text=f'Категория товара: {data["category"]}', callback_data='update_category')
    ikb.button(text=f'Название товара: {data["name"]}', callback_data='update_name')
    ikb.button(text=f'Описание товара: {data["description"]}', callback_data='update_description')
    ikb.button(text=f'Цена товара: {data["price"]}', callback_data='update_price')
    ikb.button(text='Изображение товара', callback_data='update_image')
    ikb.button(text='Посмотреть результат изменений', callback_data='update_result')
    ikb.button(text='Назад ⬅️', callback_data=f'cancel_update')
    ikb.adjust(1)

    return ikb.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
    )


async def create_cancel_update() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardBuilder()
    ikb.button(text=f'Назад ⬅️', callback_data=f'cancel_update_value')

    return ikb.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
    )
