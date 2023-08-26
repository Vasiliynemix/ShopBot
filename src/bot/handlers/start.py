from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from src.bot.filters.register_filter import RegisterFilter, AdminFilter, ModeratorFilter
from src.bot.middlewares.user import UserMiddleware
from src.bot.structures.keyboards.user_kb import create_main_user_kb
from src.db.models import User

router = Router()

router.message.middleware(UserMiddleware())


@router.message(CommandStart(), RegisterFilter())
async def start_handler_first(message: types.Message, user: User):
    return await message.answer(
        'Hi, telegram! Авторизируйся!',
        reply_markup=await create_main_user_kb(user=user)
    )


@router.message(CommandStart(), AdminFilter())
async def start_handler_admin(message: types.Message, user: User):
    return await message.answer(
        f'Привет, <b>{user.user_name}</b>!\n'
        f'<b>Твой id:</b> {message.from_user.id}\n'
        f'<b>Вы являетесь админом этого бота!</b>\n'
        f'Для того, чтобы войти в панель админа нажмите нопку "<b>Админ-панель</b>" или введите команду /admin',
        reply_markup=await create_main_user_kb(user=user)
    )


@router.message(CommandStart(), ModeratorFilter())
async def start_handler_moder(message: types.Message, user: User):
    return await message.answer(
        f'Привет, <b>{user.user_name}</b>!\n'
        f'<b>Твой id:</b> {message.from_user.id}\n'
        f'<b>Вы являетесь модератором этого бота!</b>\n'
        f'Для того, чтобы войти в панель админа нажмите нопку "<b>Админ-панель</b>" или введите команду /admin',
        reply_markup=await create_main_user_kb(user=user)
    )


@router.message(CommandStart())
async def start_handler_user(message: types.Message, user: User):
    return await message.answer(
        f'Привет, {user.user_name}!\nТвой id: {message.from_user.id}\nВы обычный пользователь',
        reply_markup=await create_main_user_kb(user=user)
    )
