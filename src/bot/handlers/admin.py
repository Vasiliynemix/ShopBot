from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.bot.filters.admin import CallBackAdminListFilter
from src.bot.filters.register_filter import AdminFilter
from src.bot.structures.keyboards.admin_kb import get_moderators_ikb, create_main_kb
from src.bot.structures.state.admin import AdminFSM
from src.db.database import Database

router = Router()


@router.message(Command(commands=['moderators']), AdminFilter())
async def list_moderators_handler(message: Message, db: Database):
    moderators = await db.user.get_by_role()
    await message.answer(
        'Список модераторов и админов группы\nДля того, чтобы удалить модератора нажмите на соответствующую кнопку',
        reply_markup=await get_moderators_ikb(moderators=moderators)
    )


@router.callback_query(CallBackAdminListFilter.filter(), AdminFilter())
async def delete_moderator_handler(call: CallbackQuery, db: Database):
    await db.user.remove_role(user_id=int(call.data[10:]))
    await call.answer()
    moderators = await db.user.get_by_role()
    await call.message.edit_text(
        'Список модераторов и админов группы\nДля того, чтобы удалить модератора нажмите на соответствующую кнопку',
        reply_markup=await get_moderators_ikb(moderators=moderators)
    )


@router.callback_query(F.data == 'add_moderator', AdminFilter())
async def new_moderator_handler(call: CallbackQuery, state: FSMContext):
    await state.set_state(AdminFSM.add_admin)
    await call.answer()
    await call.message.edit_text('Введите id пользователя, которого хотите добавить в модераторы')


@router.message(AdminFSM.add_admin, AdminFilter())
async def get_id_new_moderator_handler(message: Message, db: Database, state: FSMContext):
    await state.clear()
    await db.user.update_role(user_id=int(message.text), message=message)
    moderators = await db.user.get_by_role()
    await message.answer(
        'Список модераторов и админов группы\nДля того, чтобы удалить модератора нажмите на соответствующую кнопку',
        reply_markup=await get_moderators_ikb(moderators=moderators)
    )


@router.callback_query(F.data == 'start_menu', AdminFilter())
async def basic_menu_handler(call: CallbackQuery):
    await call.message.edit_text('Меню', reply_markup=create_main_kb())
