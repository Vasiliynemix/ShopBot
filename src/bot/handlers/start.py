from aiogram import Router, types, Bot
from aiogram.filters import CommandStart

from src.bot.filters.register_filter import RegisterFilter, AdminFilter, ModeratorFilter
from src.bot.structures.lexicon.lexicon_ru import MainMenu
from src.db.models import User

router = Router()


@router.message(CommandStart(), RegisterFilter())
async def start_handler(message: types.Message):
    return await message.answer(
        'Hi, telegram! Авторизируйся!'
    )


@router.message(CommandStart(), AdminFilter())
async def start_handler(message: types.Message, bot: Bot):
    await MainMenu(bot).get_menu_admin()
    return await message.answer(
        f'Hi, telegram! {message.from_user.id}, Вы являетесь админом этого бота!'
    )


@router.message(CommandStart(), ModeratorFilter())
async def start_handler(message: types.Message, bot: Bot):
    await MainMenu(bot).get_menu_moderator()
    return await message.answer(
        f'Hi, telegram! {message.from_user.id}, Вы являетесь модератором'
    )


@router.message(CommandStart())
async def start_handler(message: types.Message, bot: Bot):
    await MainMenu(bot).get_menu_user()
    return await message.answer(
        f'Hi, telegram! {message.from_user.id}, Вы обычный пользователь'
    )
