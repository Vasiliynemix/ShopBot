from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto

from src.bot.filters.user import CallBackCategoriesListFilter
from src.bot.structures.keyboards.admin_kb import get_categories_ikb
from src.bot.structures.lexicon.lexicon_ru import create_text_product
from src.bot.structures.states.user import UserFSM
from src.db.database import Database

router = Router()


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
async def user_menu(call: CallbackQuery, state: FSMContext, db: Database, bot: Bot):
    await call.answer()
    category_name = call.data[9:]
    await state.set_state(UserFSM.catalog)
    products = await db.product.get_products(category_name=category_name)
    media_group = [
        InputMediaPhoto(media='https://drive.google.com/file/d/1qHd9biv9RtPEg_aTS_WO9BmpXrWUgcL_/view?usp=drive_link'),
        InputMediaPhoto(media='https://drive.google.com/file/d/1qHd9biv9RtPEg_aTS_WO9BmpXrWUgcL_/view?usp=drive_link')
    ]
    for product in products:
        await bot.send_media_group(chat_id=call.from_user.id, media=media_group)
        await call.message.answer(
            text=await create_text_product(
                name=product.name,
                description=product.description,
                price=product.price
            ),
            # reply_markup=await get_categories_ikb(categories=products)
        )
# Список товаров в категории ===========================================================
