from aiogram import Router, types
from aiogram.filters import Command

from src.bot.filters.register_filter import AdminFilter, ModeratorFilter
from src.bot.structures.lexicon.lexicon_ru import COMMAND_HELP

router = Router()


@router.message(Command(commands=['help']), AdminFilter())
async def start_handler(message: types.Message):
    text = COMMAND_HELP['help_admin']
    return await message.answer(text=text)


@router.message(Command(commands=['help']), ModeratorFilter())
async def start_handler(message: types.Message):
    text = COMMAND_HELP['help_moderator']
    return await message.answer(text=text)


@router.message(Command(commands=['help']))
async def start_handler(message: types.Message):
    text = COMMAND_HELP['help_user']
    return await message.answer(text=text)
