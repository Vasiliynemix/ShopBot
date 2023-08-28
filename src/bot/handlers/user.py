from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto

from src.bot.filters.user import CallBackCategoriesListFilter, ProductMenuFilter
from src.bot.structures.keyboards.admin_kb import get_categories_ikb, requests_add_status_moderator
from src.bot.structures.keyboards.user_kb import create_main_user_kb, create_product_kb
from src.bot.structures.lexicon.lexicon_ru import create_text_product
from src.bot.structures.states.user import UserFSM
from src.configuration import conf
from src.db.database import Database

router = Router()


# Попросить статут модератора =========================================================
@router.message(F.text == 'Получить модератора 🙇')
async def request_status_moderator(message: Message, bot: Bot, db: Database):
    user = await db.user.get_by_user_id(user_id=message.from_user.id)
    if user.request_status_moder == 1:
        return await message.answer(
            'Вам уже отказали! напишите администратору,'
            ' чтобы он добавил для вас роль модератора, если это произошло по ошибке',
            reply_markup=await create_main_user_kb(user=user)
        )

    await message.answer('Вам придет сообщение от бота о принятии или отказе вашей заявки\nОжидайте')

    text = (f'Вам пришла заявка на добавление на добавление режима модератора от пользователя:\n'
            f'  id пользователя: {user.user_id}\n'
            f'  username пользователя: @{user.user_name}')

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
async def product_list(call: CallbackQuery, state: FSMContext, db: Database, bot: Bot):
    await call.answer()
    await call.message.delete()
    category_name = call.data[9:]
    await state.set_state(UserFSM.product)
    products = await db.product.get_products(category_name=category_name)
    for product in products:

        caption = await create_text_product(
                name=product.name,
                description=product.description,
                price=product.price,
                volume=product.volume
            )

        photo = await db.image.get_by_product_fk(product_fk=product.id)

        await bot.send_photo(
            chat_id=call.from_user.id,
            photo=photo,
            caption=caption,
            reply_markup=await create_product_kb(product_name=product.name)
        )


# Список товаров в категории ===========================================================


# Добавление товара в корзину ==========================================================
@router.callback_query(ProductMenuFilter.filter(), UserFSM.product)
async def add_product_in_basket(call: CallbackQuery):
    await call.answer()
    await call.message.delete()
    data = call.data[13:]
    await call.message.answer(f'товар: {data} добавлен в корзину!')


# Добавление товара в корзину ==========================================================


@router.message()
async def error_message(message: Message):
    await message.answer('Нет такого варианта!')
