import stat

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.bot.filters.admin import CallBackCategoriesListFilter
from src.bot.filters.register_filter import ModeratorFilter
from src.bot.structures.keyboards.admin_kb import add_product_in_db, create_main_kb, get_categories_ikb
from src.bot.structures.state.moderator import AddProduct, AddCategory
from src.db.database import Database

router = Router()


@router.message(Command(commands=['admin']), ModeratorFilter())
async def start_added_product(message: Message, state: FSMContext):
    await state.set_state(AddProduct.name)
    await message.answer('Введите название товара')


@router.message(AddProduct.name, ModeratorFilter())
async def add_name_product(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddProduct.description)
    await message.answer('Введите описание товара')


@router.message(AddProduct.description, ModeratorFilter())
async def add_description_product(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddProduct.price)
    await message.answer('Введите цену товара')


@router.message(AddProduct.price, ModeratorFilter())
async def add_price_product(message: Message, state: FSMContext, db: Database):
    await state.update_data(price=message.text)
    await state.set_state(AddProduct.category)
    categories = await db.category.get_categories()
    await message.answer(
        'Выберите категорию, которой пренадлежит товар или добавьте новую',
        reply_markup=await get_categories_ikb(categories=categories),
    )


@router.callback_query(F.data == 'add_category', AddProduct.category, ModeratorFilter())
async def add_new_category_in_db(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(AddCategory.new_category)
    await call.message.edit_text('Введите название категории без ошибок')


@router.message(AddCategory.new_category, ModeratorFilter())
async def add_new_category_in_db(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    data = await state.get_data()
    await state.set_state(AddProduct.result)
    text = (f'название: {data["name"]}\nописание: {data["description"]}\n'
            f'цена: {data["price"]}\nкатегория: {data["category"]}')
    await message.answer(
        text=text,
        reply_markup=await add_product_in_db()
    )


@router.callback_query(AddProduct.category, ModeratorFilter(), CallBackCategoriesListFilter.filter())
async def add_category_product(call: CallbackQuery, state: FSMContext):
    await state.update_data(category=call.data[9:])
    data = await state.get_data()
    await state.set_state(AddProduct.result)
    text = (f'название: {data["name"]}\nописание: {data["description"]}\n'
            f'цена: {data["price"]}\nкатегория: {data["category"]}')

    await call.message.edit_text(
        text=text,
        reply_markup=await add_product_in_db()
    )


@router.callback_query(F.data == 'product_publish', AddProduct.result, ModeratorFilter())
async def publish_product(call: CallbackQuery, state: FSMContext, db: Database):
    await call.answer()
    data = await state.get_data()
    await db.product.new(
        name=data['name'],
        description=data['description'],
        price=float(data['price']),
        category=data['category'],
    )
    await state.clear()
    await call.message.edit_text('Опубликовано')


@router.callback_query(F.data == 'product_update', AddProduct.result, ModeratorFilter())
async def update_add_product(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    await state.get_state()
    await call.message.edit_text('Выбери из списка что хочешь изменить')


@router.callback_query(F.data == 'product_cancel', AddProduct.result, ModeratorFilter())
async def cancel_add_product(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.clear()
    await call.message.edit_text('Меню', reply_markup=await create_main_kb())
