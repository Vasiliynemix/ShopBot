from aiogram.filters import BaseFilter
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.structures.role import Role
from src.configuration import conf
from src.db.database import Database


class RegisterFilter(BaseFilter):
    async def __call__(self, *args, **kwargs):
        async with AsyncSession(bind=kwargs['engine']) as session:
            db = Database(session)
            message = kwargs['event_from_user']
            if await db.user.get_by_user_id(message.id) is not None:
                return False
            else:
                if message.id == conf.admin.admin_id:
                    await db.user.new(
                        user_id=message.id,
                        language_code=message.language_code,
                        role=Role.ADMINISTRATOR,
                        user_name=message.username,
                    )
                else:
                    await db.user.new(
                        user_id=message.id,
                        language_code=message.language_code,
                        user_name=message.username,
                    )
                await db.session.commit()
        return True


class AdminFilter(BaseFilter):
    async def __call__(self, *args, **kwargs):
        async with AsyncSession(bind=kwargs['engine']) as session:
            db = Database(session)
            message = kwargs['event_from_user']
            user = await db.user.get_by_user_id(message.id)
            if user.role == Role.ADMINISTRATOR:
                return True


class ModeratorFilter(BaseFilter):
    async def __call__(self, *args, **kwargs):
        async with AsyncSession(bind=kwargs['engine']) as session:
            db = Database(session)
            message = kwargs['event_from_user']
            user = await db.user.get_by_user_id(message.id)
            if user.role == Role.MODERATOR or user.role == Role.ADMINISTRATOR:
                return True
