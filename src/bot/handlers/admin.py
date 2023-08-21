from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.filters.register_filter import AdminFilter
from src.db.database import Database

router = Router()


@router.message(Command(commands=['moderators']), AdminFilter())
async def help_handler(message: Message, db: Database):
    moderators = await db.user.get_by_role()
    message_answer = ''
    for user in moderators:
        message_answer += f'{user.user_id}\n'
    await message.answer(message_answer)


@router.message(Command(commands=['admin']), AdminFilter())
async def help_handler(message: Message, db: Database):
    await db.user.update_role(user_id=message.from_user.id)
    await message.answer('qwerty')
