from aiogram import Router, types
from aiogram.filters import CommandStart

from src.bot.filters.register_filter import RegisterFilter, AdminFilter, ModeratorFilter

router = Router()


@router.message(CommandStart(), RegisterFilter())
async def start_handler(message: types.Message):
    return await message.answer(
        'Hi, telegram! Авторизируйся!'
    )


@router.message(CommandStart(), AdminFilter())
async def start_handler(message: types.Message):
    return await message.answer(
        f'Hi, telegram! {message.from_user.id}, Вы являетесь админом этого бота!'
    )


@router.message(CommandStart(), ModeratorFilter())
async def start_handler(message: types.Message):
    return await message.answer(
        f'Hi, telegram! {message.from_user.id}, Вы являетесь модератором'
    )


@router.message(CommandStart())
async def start_handler(message: types.Message):
    return await message.answer(
        f'Hi, telegram! {message.from_user.id}, Вы обычный пользователь'
    )
