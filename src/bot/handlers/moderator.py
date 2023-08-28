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


# ДОБАВЛЕНИЕ ТОВАРА ======================================================================
# название товара ========================================================================
@router.callback_query(Moderator.start, F.data == 'add_product_in_db', ModeratorFilter())
async def start_added_product(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(AddProduct.name)
    await call.message.edit_text('Введите название товара')


# название товара ========================================================================


# количество товара на складе ============================================================
@router.message(AddProduct.name, ModeratorFilter())
async def add_name_product(message: Message, state: FSMContext, db: Database):
    product_name = await db.product.get_product_name(product_name=message.text)

    if product_name is not None:
        return await message.answer('Такое имя товара уже используется, введите другое!')

    await state.update_data(name=message.text)
    await state.set_state(AddProduct.volume)
    await message.answer('Введите количество товара на складе на данный момент')


# количество товара на складе ============================================================


# описание товара товара ================================================================
@router.message(AddProduct.volume, ModeratorFilter())
async def start_added_product(message: Message, state: FSMContext):
    try:
        int(message.text)
        await state.update_data(volume=message.text)
        await state.set_state(AddProduct.description)
        await message.answer('Введите описание товара')
    except ValueError:
        await message.answer('ВВедите целое число!')


# описание товара товара ================================================================


# цена товара ===========================================================================
@router.message(AddProduct.description, ModeratorFilter())
async def add_description_product(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddProduct.price)
    await message.answer('Введите цену товара')

# цена товара ===========================================================================


# КАТЕГОРИЯ ТОВАРА =================================new_category=====================================
# выбор категории товара ================================================================
@router.message(AddProduct.price, ModeratorFilter())
async def add_price_product(message: Message, state: FSMContext, db: Database):
    try:
        float(message.text)
        await state.update_data(price=message.text)
        await state.set_state(AddProduct.category)
        categories = await db.category.get_categories()
        await message.answer(
            'Выберите категорию, которой принадлежит товар или добавьте новую',
            reply_markup=await get_categories_ikb(categories=categories, is_admin_mode=True),
        )
    except ValueError:
        await message.answer('Введите число!')


# выбор категории товара =================================================================


# Добавление категории товара из базы данных в память бота ===============================
@router.callback_query(AddProduct.category, ModeratorFilter(), CallBackCategoriesListFilter.filter())
@router.callback_query(
    CallBackCategoriesListFilter.filter(),
    ModeratorFilter(),
)
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

    return await call.message.edit_text(
        'Выбери из списка что хочешь изменить',
        reply_markup=await create_update_kb(data=data)
    )


# Добавление категории товара из базы данных в память бота ===============================


# Добавление новой категории в память бота ===============================================
@router.callback_query(F.data == 'add_category', AddProduct.category, ModeratorFilter())
@router.callback_query(UpdateProduct.update_category, ModeratorFilter(), F.data == 'add_category')
async def add_new_category(call: CallbackQuery, state: FSMContext):
    await call.answer()

    current_state = await state.get_state()

    if current_state == AddProduct.category:
        await state.set_state(AddCategory.new_category)
    else:
        await state.set_state(UpdateProduct.new_category)

    await call.message.edit_text('Введите название категории без ошибок')


# Добавление новой категории в память бота ===============================================
# КАТЕГОРИЯ ТОВАРА =======================================================================


# ИЗОБРАЖЕНИЕ ТОВАРА =====================================================================
# добавление изображения товара ==========================================================
@router.message(AddCategory.new_category, ModeratorFilter())
async def add_new_category_in_db(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await state.set_state(AddProduct.image)
    await message.answer(
        'Добавьте изображения товара\n'
        'После того, как добавите изображение нажмите на кнопку "Продолжить ✅" ниже'
    )


# добавление изображения товара ==========================================================


# добавление изображения товара в память бота ============================================
@router.message(AddProduct.image, ModeratorFilter(), F.photo)
async def add_image_in_redis(message: Message, bot: Bot, state: FSMContext, storage: RedisStorage):
    await state.set_state(AddProduct.test_publish)
    await static.save_image_in_redis(message=message, bot=bot, storage=storage)
    return await message.answer('изображение добавлено!', reply_markup=await save_images_in_static())


# добавление изображения товара в память бота ============================================
# ИЗОБРАЖЕНИЕ ТОВАРА =====================================================================


# Проверка товара ========================================================================
@router.callback_query(AddProduct.test_publish, F.data == 'product_test_publish', ModeratorFilter())
@router.callback_query(UpdateProduct.update, F.data == 'update_result', ModeratorFilter())
@router.callback_query(F.data == 'cancel_update', UpdateProduct.update, ModeratorFilter())
async def test_public_product(call: CallbackQuery, bot: Bot, state: FSMContext, storage: RedisStorage):
    await call.answer()
    await state.set_state(AddProduct.result)

    # нажатие кнопки назад(cancel_update) ================================================
    if call.data == 'cancel_update':
        return await call.message.edit_text(
            text='Выберите один из вариантов ниже',
            reply_markup=await add_product_in_db()
        )
    # нажатие кнопки назад(cancel_update) ================================================

    await call.message.delete()
    data = await state.get_data()

    # текст товара =======================================================================
    caption = await create_text_product(
        name=data['name'],
        volume=data['volume'],
        description=data['description'],
        price=data['price'],
        category=data['category'],
    )
    photo = await static.public_image(message=call, storage=storage)
    await bot.send_photo(chat_id=call.from_user.id, photo=photo, caption=caption)
    return await call.message.answer(
        text='Выберите один из вариантов ниже',
        reply_markup=await add_product_in_db()
    )


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

    # сохранение в базу данных ===========================================================
    image = await static.get_redis_value(message=call, storage=storage)
    await db.product.new(
        name=data['name'],
        description=data['description'],
        price=float(data['price']),
        volume=int(data['volume']),
        category=data['category'],
        image=image
    )

    user = await db.user.get_by_user_id(user_id=call.from_user.id)
    await call.message.answer('Товар опубликован!', reply_markup=await create_main_user_kb(user=user))


# Публикация товара ======================================================================


# ОБНОВЛЕНИЕ ТОВАРА ======================================================================
# меню позиций товара ====================================================================
@router.callback_query(F.data == 'product_update', AddProduct.result, ModeratorFilter())
async def update_add_product(call: CallbackQuery, state: FSMContext):
    await call.answer()

    data = await state.get_data()

    await state.set_state(UpdateProduct.update)
    await call.message.edit_text(
        'Выбери из списка что хочешь изменить',
        reply_markup=await create_update_kb(data=data)
    )


# меню позиций товара ====================================================================


# обновления товара ======================================================================
@router.message(UpdateProduct.update_one_value, ModeratorFilter())
async def update_value(
        message: Message,
        state: FSMContext,
        storage: RedisStorage,
        bot: Bot, db: Database
):
    # получения и обновление нужной позиции товара(update_position) ======================
    update_position = await update_product.get_update_value_in_key(chat_id=message.from_user.id, storage=storage)
    if update_position == 'name':
        product_name = await db.product.get_product_name(product_name=message.text)

        if product_name is None:
            return await message.answer('Такое имя товара уже используется, введите другое!')

        await state.update_data(name=message.text)

    elif update_position == 'description':
        await state.update_data(description=message.text)

    elif update_position == 'price':
        try:
            float(message.text)
            await state.update_data(price=message.text)
        except ValueError:
            await message.answer('Введите число!')

    elif update_position == 'volume':
        try:
            float(message.text)
            await state.update_data(volume=message.text)
        except ValueError:
            await message.answer('Введите целое число!')
    # получения и обновление нужной позиции товара(update_position) ======================

    data = await state.get_data()

    # удаление сообщения ввода нового названия для позиции товара(с кнопкой назад) ======
    message_id_for_delete = await change_message.get_value_in_key(chat_id=message.from_user.id, storage=storage)
    await change_message.delete_message(
        chat_id=message.from_user.id,
        message_id=message_id_for_delete,
        bot=bot,
        storage=storage
    )

    if update_position == 'image':
        if message.photo is None:
            return await message.answer(
                'Это не фото, добавьте фото пожалуйста',
                reply_markup=await create_cancel_update()
            )
        await static.save_image_in_redis(message=message, bot=bot, storage=storage)

    await state.set_state(UpdateProduct.update)

    return await message.answer(
        'Выбери из списка что хочешь изменить',
        reply_markup=await create_update_kb(data=data)
    )


# обновления товара ======================================================================


# ПОЗИЦИИ ТОВАРА ДЛЯ ИЗМЕНЕНИЯ ===========================================================
# список позиций товара ==================================================================
@router.message(UpdateProduct.new_category, ModeratorFilter(), F.text)
async def update_add_new_category(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await state.set_state(UpdateProduct.update)

    data = await state.get_data()

    await message.answer(
        'Выбери из списка что хочешь изменить',
        reply_markup=await create_update_kb(data=data)
    )


# список позиций товара ==================================================================


# возвращение в меню списка позиций товара для обновления ================================
@router.callback_query(F.data == 'cancel_update_value', UpdateProduct.update_one_value, ModeratorFilter())
@router.callback_query(F.data == 'cancel_update_value', UpdateProduct.update_category, ModeratorFilter())
async def cancel_update_value(call: CallbackQuery, state: FSMContext, storage: RedisStorage):
    data = await state.get_data()

    # удаление из памяти бота выбранную позицию товара ===================================
    update_redis_key = await update_product.redis_key_for_update_value(chat_id=call.from_user.id)
    await update_product.delete_redis_key_for_update(key=update_redis_key, storage=storage)

    await state.set_state(UpdateProduct.update)

    await call.message.edit_text(
        'Выбери из списка что хочешь изменить',
        reply_markup=await create_update_kb(data=data)
    )


# возвращение в меню списка позиций товара для обновления ================================


# Изменить категорию товара =============================================================
@router.callback_query(F.data == 'update_category', UpdateProduct.update, ModeratorFilter())
async def update_category(call: CallbackQuery, state: FSMContext, storage: RedisStorage, db: Database):
    await call.answer()

    # добавление в память бота выбранную позицию товара, на которую будет обновлен товар =
    await update_product.add_update_value(chat_id=call.from_user.id, storage=storage, value=call.data)

    categories = await db.category.get_categories()

    await state.set_state(UpdateProduct.update_category)
    await call.message.edit_text(
        'Выберите новую категорию товара, добавьте новую категорию или отмените изменение позиции товара',
        reply_markup=await get_categories_ikb(
            categories=categories,
            is_admin_mode=True,
            is_update_mode=True
        )
    )


# Изменить категорию товара =============================================================


# Изменение имени | описания | цены | изображения товара =================================
@router.callback_query(F.data == 'update_name', UpdateProduct.update, ModeratorFilter())
@router.callback_query(F.data == 'update_description', UpdateProduct.update, ModeratorFilter())
@router.callback_query(F.data == 'update_price', UpdateProduct.update, ModeratorFilter())
@router.callback_query(F.data == 'update_image', UpdateProduct.update, ModeratorFilter())
@router.callback_query(F.data == 'update_volume', UpdateProduct.update, ModeratorFilter())
async def update_description(call: CallbackQuery, state: FSMContext, storage: RedisStorage):
    await call.answer()

    # добавления ид сообщения для ввода новой позиции товара(с кнопкой назад) ============
    message_id = call.message.message_id
    await change_message.add_message_id_in_redis(
        chat_id=call.from_user.id,
        message_id=message_id,
        storage=storage
    )

    # добавление в память бота выбранную позицию товара, на которую будет обновлен товар =
    await update_product.add_update_value(chat_id=call.from_user.id, storage=storage, value=call.data)

    await state.set_state(UpdateProduct.update_one_value)
    if call.data == 'update_image':
        return await call.message.edit_text(
            'Добавьте новое изображение для товара или нажмите назад для возвращение в прошлое меню',
            reply_markup=await create_cancel_update()
        )

    return await call.message.edit_text(
        'Введите новое название выбранной позиции товара или нажмите назад для возвращение в прошлое меню',
        reply_markup=await create_cancel_update()
    )


# Изменение имени | описания | цены | изображения товара =================================
# ПОЗИЦИИ ТОВАРА ДЛЯ ИЗМЕНЕНИЯ ===========================================================
# ОБНОВЛЕНИЕ ТОВАРА ======================================================================


# Отмена публикации товара ===============================================================
@router.callback_query(F.data == 'product_cancel', AddProduct.result, ModeratorFilter())
async def cancel_add_product(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.clear()
    await state.set_state(Moderator.start)
    await call.message.edit_text(
        'Выберите из списка что хотите сделать',
        reply_markup=await start_admin_kb()
    )

# Отмена публикации товара ===============================================================
# ДОБАВЛЕНИЕ ТОВАРА ======================================================================
