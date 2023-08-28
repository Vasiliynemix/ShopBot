from aiogram.types import Message
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.structures.role import Role
from src.configuration import conf
from src.db.models import User
from src.db.repositories.abstract import Repository


class UserRepo(Repository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=User, session=session)

    async def new(
            self,
            user_id: int,
            user_name: str | None = None,
            first_name: str | None = None,
            second_name: str | None = None,
            language_code: str | None = None,
            is_premium: bool | None = False,
            role: Role | None = Role.USER,
    ) -> None:
        await self.session.merge(
            User(
                user_id=user_id,
                user_name=user_name,
                first_name=first_name,
                second_name=second_name,
                language_code=language_code,
                is_premium=is_premium,
                role=role,
            )
        )

    async def get_by_user_id(self, user_id: int):
        return await self.session.scalar(select(User).where(User.user_id == user_id).limit(1))

    async def get_admin_users(self):
        moderators = await self.session.scalars(
            select(User).filter(
                or_(
                    User.role == Role.ADMINISTRATOR,
                    User.role == Role.MODERATOR
                )
            )
        )
        return moderators.all()

    async def update_role(self, user_id: int, message: Message = None) -> bool:
        if not user_id == conf.admin.admin_id:
            user = await self.get_by_user_id(user_id=user_id)
            if user is None:
                await message.answer('Такого пользователя не существует в базе бота\nНажмите еще раз на кнопку и '
                                     'введите корректные данные')
            else:
                user.role = Role.MODERATOR
                await self.session.commit()
        return True

    async def update_request_status(self, user_id: int) -> bool:
        user = await self.get_by_user_id(user_id=user_id)
        user.request_status_moder = 1
        await self.session.commit()
        return True

    async def remove_role(self, user_id: int) -> bool:
        if not user_id == conf.admin.admin_id:
            user = await self.get_by_user_id(user_id=user_id)
            user.role = Role.USER
            await self.session.commit()
        return True
