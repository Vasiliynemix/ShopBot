from aiogram import Router, types
from aiogram.filters import CommandStart

from src.bot.filters.register_filter import RegisterFilter, AdminFilter, ModeratorFilter
from src.bot.structures.keyboards.user_kb import create_main_user_kb

router = Router()


@router.message(CommandStart(), RegisterFilter())
async def start_handler_first(message: types.Message):
    return await message.answer(
        'Hi, telegram! Авторизируйся!',
        reply_markup=await create_main_user_kb()
    )


@router.message(CommandStart(), AdminFilter())
async def start_handler_admin(message: types.Message):
    return await message.answer(
        f'Hi, telegram! {message.from_user.id}, Вы являетесь админом этого бота!'
    )


@router.message(CommandStart(), ModeratorFilter())
async def start_handler_moder(message: types.Message):
    return await message.answer(
        f'Hi, telegram! {message.from_user.id}, Вы являетесь модератором'
    )


@router.message(CommandStart())
async def start_handler_user(message: types.Message):
    return await message.answer(
        f'Hi, telegram! {message.from_user.id}, Вы обычный пользователь',
        reply_markup=await create_main_user_kb()
    )
