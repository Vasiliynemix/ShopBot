from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from src.bot.common.images import static
from src.bot.common.message import change_message
from src.bot.filters.register_filter import ModeratorFilter
from src.bot.filters.user import CallBackCategoriesListFilter
from src.bot.structures.keyboards.admin_kb import add_product_in_db, get_categories_ikb, save_images_in_static, \
    start_admin_kb
from src.bot.structures.keyboards.user_kb import create_main_user_kb
from src.bot.structures.lexicon.lexicon_ru import create_text_product
from src.bot.structures.states.moderator import AddProduct, AddCategory, Moderator, UpdateProduct
from src.db.database import Database
from src.db.models import User

router = Router()


# Админ панель ===========================================================================
@router.message(F.text == 'Админ-панель', ModeratorFilter())
@router.message(Command(commands=['admin']), ModeratorFilter())
async def start_admin_panel(message: Message, state: FSMContext, storage: RedisStorage):
    await state.clear()
    await static.delete_redis_key_for_images(message=message, storage=storage)
    await state.set_state(Moderator.start)
    await message.answer('Выберите из списка что хотите сделать', reply_markup=await start_admin_kb())


# Админ панель ===========================================================================


# Старт добавления товара ================================================================
@router.callback_query(Moderator.start, F.data == 'add_product_in_db', ModeratorFilter())
async def start_added_product(call: CallbackQuery, state: FSMContext):
    # await call.message.delete()
    await call.answer()
    await state.set_state(AddProduct.name)
    await call.message.edit_text('Введите название товара')


# Старт добавления товара ================================================================


# Название товара ========================================================================
@router.message(AddProduct.name, ModeratorFilter())
async def add_name_product(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddProduct.description)
    await message.answer('Введите описание товара')


# Название товара ========================================================================


# Описание товара ========================================================================
@router.message(AddProduct.description, ModeratorFilter())
async def add_description_product(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddProduct.price)
    await message.answer('Введите цену товара(число)')


# Описание товара ========================================================================


# Цена товара ============================================================================
@router.message(AddProduct.price, ModeratorFilter())
async def add_price_product(message: Message, state: FSMContext, db: Database):
    await state.update_data(price=message.text)
    await state.set_state(AddProduct.category)
    categories = await db.category.get_categories()
    await message.answer(
        'Выберите категорию, которой принадлежит товар или добавьте новую',
        reply_markup=await get_categories_ikb(categories=categories, is_admin_mode=True),
    )


# Цена товара ============================================================================


# Категория товара =======================================================================
@router.callback_query(AddProduct.category, ModeratorFilter(), CallBackCategoriesListFilter.filter())
async def add_category_product(call: CallbackQuery, state: FSMContext):
    await state.update_data(category=call.data[9:])
    await state.set_state(AddProduct.image)
    await call.answer()
    await call.message.edit_text(
        'Добавьте изображения товара(без ограничений)\n'
        'После того, как добавите все изображения нажмите на кнопку "Продолжить ✅" ниже'
    )


@router.callback_query(F.data == 'add_category', AddProduct.category, ModeratorFilter())
async def add_new_category(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(AddCategory.new_category)
    await call.message.edit_text('Введите название категории без ошибок')


@router.message(AddCategory.new_category, ModeratorFilter())
async def add_new_category_in_db(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await state.set_state(AddProduct.image)
    await message.answer(
        'Добавьте изображения товара(без ограничений)\n'
        'После того, как добавите все изображения нажмите на кнопку "Продолжить ✅" ниже'
    )


# Категория товара =======================================================================


# Изображения товара =====================================================================
@router.message(AddProduct.image, ModeratorFilter(), F.photo)
async def add_image_in_redis(message: Message, bot: Bot, state: FSMContext, storage: RedisStorage):
    await state.get_state()
    await static.save_images_in_redis(message=message, bot=bot, storage=storage)
    await message.answer('изображение добавлено!', reply_markup=await save_images_in_static())


# Изображения товара =====================================================================


# Проверка товара ========================================================================
@router.message(AddProduct.image, F.text == 'Продолжить ✅', ModeratorFilter())
async def test(message: Message, bot: Bot, state: FSMContext, storage: RedisStorage):
    await message.answer("Проверьте все перед публикацией!", reply_markup=ReplyKeyboardRemove())

    data = await state.get_data()

    media_data = await static.test_answer_images(message=message, storage=storage, product_data=data, is_test=True)
    test_message = await bot.send_media_group(message.from_user.id, media=media_data)

    message_ids_list = []
    for msg in test_message:
        message_ids_list.append(msg.message_id)

    await change_message.delete_redis_key_for_message(
        key=f'redis_key_message_id:{message.from_user.id}',
        storage=storage
    )
    await change_message.add_message_id_in_redis(
        chat_id=message.from_user.id,
        message_ids_list=message_ids_list,
        storage=storage
    )

    await message.answer(text='Выберите один из вариантов ниже', reply_markup=await add_product_in_db())

    await state.set_state(AddProduct.result)


# Проверка товара ========================================================================


# Публикация товара ======================================================================
@router.callback_query(F.data == 'product_publish', AddProduct.result, ModeratorFilter())
async def publish_product(
        call: CallbackQuery,
        state: FSMContext,
        db: Database,
        storage: RedisStorage,
        bot: Bot,
):
    await call.message.delete()
    await call.answer()
    data = await state.get_data()
    await state.clear()
    product_id = await db.product.new(
        name=data['name'],
        description=data['description'],
        price=float(data['price']),
        category=data['category'],
    )
    category_name = await db.category.get_one_category(category_name=data['category'])
    await static.test_answer_images(message=call, storage=storage, product_data=data)
    await static.public_images(category_name=category_name, product_id=product_id)

    message_ids_list = await change_message.get_value_in_key(chat_id=call.from_user.id, storage=storage)
    await change_message.delete_message(
        chat_id=call.from_user.id,
        message_ids_list=message_ids_list,
        bot=bot,
        storage=storage
    )

    user = await db.user.get_by_user_id(user_id=call.from_user.id)
    await call.message.answer('Товар опубликован!', reply_markup=await create_main_user_kb(user=user))


# Публикация товара ======================================================================


@router.callback_query(F.data == 'product_update', AddProduct.result, ModeratorFilter())
async def update_add_product(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    await state.set_state(UpdateProduct.update)
    await call.message.edit_text('Выбери из списка что хочешь изменить')


@router.callback_query(F.data == 'product_cancel', AddProduct.result, ModeratorFilter())
async def cancel_add_product(call: CallbackQuery, state: FSMContext):
    await call.message.delete_reply_markup()
    await call.answer()
    await state.clear()
    await call.message.edit_text('Выберите из списка что хотите сделать', reply_markup=await start_admin_kb())
