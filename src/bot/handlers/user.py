from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto

from src.bot.filters.user import CallBackCategoriesListFilter
from src.bot.structures.keyboards.admin_kb import get_categories_ikb, requests_add_status_moderator
from src.bot.structures.lexicon.lexicon_ru import create_text_product
from src.bot.structures.states.user import UserFSM
from src.configuration import conf
from src.db.database import Database

router = Router()


# Попросить статут модератора =========================================================
@router.message(F.text == 'Получить модератора 🙇')
async def request_status_moderator(message: Message, bot: Bot, db: Database):
    await message.answer('Вам придет сообщение от бота о принятии или отказе вашей заявки\nОжидайте')

    user = await db.user.get_by_user_id(user_id=message.from_user.id)

    a = user.user_id
    b = user.user_name
    c = conf.admin.admin_id
    text = (f'Вам пришла заявка от пользователя\n'
            f'телеграм id пользователя: {user.user_id}\n'
            f'телеграм username пользователя: @{user.user_name}')

    await bot.send_message(
        chat_id=conf.admin.admin_id,
        text=text,
        reply_markup=await requests_add_status_moderator(user.user_id)
    )


# Попросить статут модератора =========================================================


# Список категорий =====================================================================
@router.message(F.text == 'Каталог')
async def user_menu(message: Message, state: FSMContext, db: Database):
    await state.set_state(UserFSM.catalog)
    categories = await db.category.get_categories()
    await message.answer(
        'Выберите категорию из списка',
        reply_markup=await get_categories_ikb(categories=categories)
    )


# Список категорий =====================================================================


# Список товаров в категории ===========================================================
@router.callback_query(CallBackCategoriesListFilter.filter(), UserFSM.catalog)
async def user_menu(call: CallbackQuery, state: FSMContext, db: Database):
    await call.answer()
    await call.message.delete()
    category_name = call.data[9:]
    await state.set_state(UserFSM.catalog)
    products = await db.product.get_products(category_name=category_name)
    for product in products:
        await call.message.answer(
            text=await create_text_product(
                name=product.name,
                description=product.description,
                price=product.price,
                category=category_name
            )
        )
# Список товаров в категории ===========================================================


@router.message()
async def error_message(message: Message):
    await message.answer('Нет такого варианта!')
