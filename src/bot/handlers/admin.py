import re

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.bot.filters.admin import CallBackAdminListFilter, CallBackRequestStatusModeratorFilter
from src.bot.filters.register_filter import AdminFilter
from src.bot.middlewares.user import UserMiddleware
from src.bot.structures.keyboards.admin_kb import get_moderators_ikb
from src.bot.structures.keyboards.user_kb import create_main_user_kb
from src.bot.structures.states.admin import AdminFSM
from src.db.database import Database
from src.db.models import User

router = Router()

router.callback_query.middleware(UserMiddleware())


@router.message(Command(commands=['moderators']), AdminFilter())
async def list_moderators_handler(message: Message, db: Database):
    moderators = await db.user.get_admin_users()
    await message.answer(
        'Список модераторов и админов группы\nДля того, чтобы удалить модератора нажмите на соответствующую кнопку',
        reply_markup=await get_moderators_ikb(moderators=moderators)
    )


@router.callback_query(CallBackRequestStatusModeratorFilter.filter(), AdminFilter())
async def request_status_moderator(call: CallbackQuery, db: Database, bot: Bot):
    await call.answer()
    await call.message.delete()
    pattern = '[0-9]+'
    user_id = int(re.search(pattern=pattern, string=call.data)[0])
    if 'accept' in call.data:
        await db.user.update_role(user_id=user_id)

        user = await db.user.get_by_user_id(user_id=user_id)
        await bot.send_message(
            chat_id=user_id,
            text='Ваша заявка на статут модератора одобрена! Пользуйтесь.',
            reply_markup=await create_main_user_kb(user=user)
        )
    else:
        await db.user.update_request_status(user_id=user_id)

        user = await db.user.get_by_user_id(user_id=user_id)
        await bot.send_message(
            chat_id=user_id,
            text='Ваша заявка на статут модератора отклонена, извините.',
            reply_markup=await create_main_user_kb(user=user)
        )


@router.callback_query(CallBackAdminListFilter.filter(), AdminFilter())
async def delete_moderator_handler(call: CallbackQuery, db: Database):
    await db.user.remove_role(user_id=int(call.data[10:]))
    await call.answer()
    moderators = await db.user.get_admin_users()
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
    moderators = await db.user.get_admin_users()
    await message.answer(
        'Список модераторов и админов группы\nДля того, чтобы удалить модератора нажмите на соответствующую кнопку',
        reply_markup=await get_moderators_ikb(moderators=moderators)
    )


@router.callback_query(F.data == 'start_menu', AdminFilter())
async def basic_menu_handler(call: CallbackQuery, user: User):
    await call.answer()
    await call.message.delete()
    await call.message.answer('Меню', reply_markup=await create_main_user_kb(user=user))
