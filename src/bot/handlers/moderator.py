from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Message, CallbackQuery

from src.bot.common.images import static
from src.bot.common.message import change_message
from src.bot.common.update import update_product
from src.bot.filters.register_filter import ModeratorFilter
from src.bot.filters.user import CallBackCategoriesListFilter
from src.bot.structures.keyboards.admin_kb import add_product_in_db, get_categories_ikb, save_images_in_static, \
    start_admin_kb, create_update_kb, create_cancel_update
from src.bot.structures.keyboards.user_kb import create_main_user_kb
from src.bot.structures.lexicon.lexicon_ru import create_text_product
from src.bot.structures.states.moderator import AddProduct, AddCategory, Moderator, UpdateProduct
from src.db.database import Database

router = Router()


# Админ панель ===========================================================================
@router.message(F.text == 'Админ-панель', ModeratorFilter())
@router.message(Command(commands=['admin']), ModeratorFilter())
async def start_admin_panel(message: Message, state: FSMContext, storage: RedisStorage):
    await state.clear()
    await static.delete_redis_key_for_images(message=message, storage=storage)
    await state.set_state(Moderator.start)
    await message.answer(
        'Выберите из списка что хотите сделать',
        reply_markup=await start_admin_kb()
    )


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
@router.callback_query(UpdateProduct.update_one_value, ModeratorFilter(), CallBackCategoriesListFilter.filter())
async def add_category_product(call: CallbackQuery, state: FSMContext):
    await state.update_data(category=call.data[9:])

    await call.answer()

    current_state = await state.get_state()
    if current_state == AddProduct.category:
        await state.set_state(AddProduct.image)
        return await call.message.edit_text(
            'Добавьте изображение товара\n'
            'После того, как добавите новое изображение нажмите "Продолжить ✅" ниже'
        )

    await state.set_state(UpdateProduct.update)
    data = await state.get_data()

    return await call.message.answer(
        'Выбери из списка что хочешь изменить',
        reply_markup=await create_update_kb(data=data)
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
        'Добавьте изображения товара\n'
        'После того, как добавите все изображения нажмите на кнопку "Продолжить ✅" ниже'
    )


# Категория товара =======================================================================


# Изображения товара =====================================================================
@router.message(AddProduct.image, ModeratorFilter(), F.photo)
async def add_image_in_redis(message: Message, bot: Bot, state: FSMContext, storage: RedisStorage):
    await state.set_state(AddProduct.test_publish)
    await static.save_image_in_redis(message=message, bot=bot, storage=storage)
    await message.answer('изображение добавлено!', reply_markup=await save_images_in_static())


# Изображения товара =====================================================================


# Проверка товара ========================================================================
@router.callback_query(AddProduct.test_publish, F.data == 'product_test_publish', ModeratorFilter())
@router.callback_query(UpdateProduct.update, F.data == 'update_result', ModeratorFilter())
async def test(call: CallbackQuery, bot: Bot, state: FSMContext, storage: RedisStorage):
    await call.answer()
    await call.message.delete()
    data = await state.get_data()

    caption = await create_text_product(
        name=data['name'],
        description=data['description'],
        price=data['price'],
        category=data['category'],
    )

    photo = await static.public_image(message=call, storage=storage, is_test=True)
    await bot.send_photo(chat_id=call.from_user.id, photo=photo, caption=caption)

    await call.message.answer(text='Выберите один из вариантов ниже', reply_markup=await add_product_in_db())

    await state.set_state(AddProduct.result)


# Проверка товара ========================================================================


# Публикация товара ======================================================================
@router.callback_query(F.data == 'product_publish', AddProduct.result, ModeratorFilter())
async def publish_product(
        call: CallbackQuery,
        state: FSMContext,
        db: Database,
        storage: RedisStorage,
):
    await call.message.delete()
    await call.answer()
    data = await state.get_data()
    await state.clear()
    await db.product.new(
        name=data['name'],
        description=data['description'],
        price=float(data['price']),
        category=data['category'],
    )

    await static.public_image(message=call, storage=storage)

    user = await db.user.get_by_user_id(user_id=call.from_user.id)
    await call.message.answer('Товар опубликован!', reply_markup=await create_main_user_kb(user=user))


# Публикация товара ======================================================================


# Меню изменения товара =================================================================
@router.callback_query(F.data == 'product_update', AddProduct.result, ModeratorFilter())
async def update_add_product(call: CallbackQuery, state: FSMContext):
    await call.answer()

    data = await state.get_data()

    await state.set_state(UpdateProduct.update)
    await call.message.edit_text(
        'Выбери из списка что хочешь изменить',
        reply_markup=await create_update_kb(data=data)
    )


@router.message(UpdateProduct.update_one_value, ModeratorFilter())
@router.message(UpdateProduct.update_image, ModeratorFilter(), F.photo)
async def update_value(message: Message, state: FSMContext, storage: RedisStorage, bot: Bot):
    update_position = await update_product.get_update_value_in_key(chat_id=message.from_user.id, storage=storage)
    if update_position == 'name':
        await state.update_data(name=message.text)
    elif update_position == 'description':
        await state.update_data(description=message.text)
    elif update_position == 'price':
        await state.update_data(price=message.text)
    elif update_position == 'category':
        await state.update_data(category=message.data[9:])
    elif update_position == 'image':
        await static.save_image_in_redis(message=message, bot=bot, storage=storage)
    else:
        pass

    data = await state.get_data()
    await state.set_state(UpdateProduct.update)

    message_id_for_delete = await change_message.get_value_in_key(chat_id=message.from_user.id, storage=storage)
    await change_message.delete_message(
        chat_id=message.from_user.id,
        message_id=message_id_for_delete,
        bot=bot,
        storage=storage
    )

    await message.answer(
        'Выбери из списка что хочешь изменить',
        reply_markup=await create_update_kb(data=data)
    )


@router.callback_query(UpdateProduct.update_one_value, ModeratorFilter(), F.data == 'add_category')
async def update_category(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(UpdateProduct.new_category)
    await call.message.edit_text('Введите название категории без ошибок')


@router.message(UpdateProduct.new_category, ModeratorFilter(), F.text)
async def update_add_new_category(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await state.set_state(UpdateProduct.update)

    data = await state.get_data()

    await message.answer(
        'Выбери из списка что хочешь изменить',
        reply_markup=await create_update_kb(data=data)
    )


@router.callback_query(F.data == 'cancel_update_value', UpdateProduct.update_one_value, ModeratorFilter())
async def cancel_update_value(call: CallbackQuery, state: FSMContext, storage: RedisStorage):
    data = await state.get_data()
    update_redis_key = await update_product.redis_key_for_update_value(chat_id=call.from_user.id)
    await update_product.delete_redis_key_for_update(key=update_redis_key, storage=storage)

    await state.set_state(UpdateProduct.update)

    await call.message.edit_text(
        'Выбери из списка что хочешь изменить',
        reply_markup=await create_update_kb(data=data)
    )


# Меню изменения товара =================================================================


# Изменить категорию товара =============================================================
@router.callback_query(F.data == 'update_category', UpdateProduct.update, ModeratorFilter())
async def update_category(call: CallbackQuery, state: FSMContext, storage: RedisStorage, db: Database):
    await call.answer()

    await update_product.add_update_value(chat_id=call.from_user.id, storage=storage, value=call.data)
    categories = await db.category.get_categories()

    await state.set_state(UpdateProduct.update_one_value)
    await call.message.edit_text(
        'Выберите новую категорию товара, добавьте новую категорию или отмените изменение позиции товара',
        reply_markup=await get_categories_ikb(
            categories=categories,
            is_admin_mode=True,
            is_update_mode=True
        )
    )


# Изменить категорию товара =============================================================


# Изменение имени | описания | цены | товара ============================================
@router.callback_query(F.data == 'update_name', UpdateProduct.update, ModeratorFilter())
@router.callback_query(F.data == 'update_description', UpdateProduct.update, ModeratorFilter())
@router.callback_query(F.data == 'update_price', UpdateProduct.update, ModeratorFilter())
async def update_description(call: CallbackQuery, state: FSMContext, storage: RedisStorage):
    await call.answer()

    message_id = call.message.message_id
    await change_message.add_message_id_in_redis(
        chat_id=call.from_user.id,
        message_id=message_id,
        storage=storage
    )

    await update_product.add_update_value(chat_id=call.from_user.id, storage=storage, value=call.data)

    await state.set_state(UpdateProduct.update_one_value)
    await call.message.edit_text(
        'Введите новое название выбранной позиции товара или нажмите назад для возвращение в прошлое меню',
        reply_markup=await create_cancel_update()
    )


# Изменение имени | описания | цены | товара ============================================


# Изменение картинку товара ==============================================================
@router.callback_query(F.data == 'update_image', UpdateProduct.update, ModeratorFilter())
async def update_image(call: CallbackQuery, state: FSMContext, storage: RedisStorage):
    await call.answer()

    message_id = call.message.message_id
    await change_message.add_message_id_in_redis(
        chat_id=call.from_user.id,
        message_id=message_id,
        storage=storage
    )

    await state.set_state(UpdateProduct.update_one_value)
    await call.message.edit_text(
        'Отправьте новое изображение товара или нажмите кнопку ниже для отмены изменения позиции товара',
        reply_markup=await create_cancel_update()
    )


# Изменение картинки товара ==============================================================
# Изменение товара =======================================================================


# Отмена публикации товара ===============================================================
@router.callback_query(F.data == 'product_cancel', AddProduct.result, ModeratorFilter())
async def cancel_add_product(call: CallbackQuery, state: FSMContext):
    # await call.message.delete_reply_markup()
    await call.answer()
    await state.clear()
    await state.set_state(Moderator.start)
    await call.message.edit_text(
        'Выберите из списка что хотите сделать',
        reply_markup=await start_admin_kb()
    )

# Отмена публикации товара ===============================================================
