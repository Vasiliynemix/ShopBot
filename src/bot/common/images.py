from uuid import uuid4

from aiogram import Bot, types
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Message, CallbackQuery, InputMediaPhoto

from src.bot.structures.lexicon.lexicon_ru import create_text_product


class Static:
    @staticmethod
    async def __redis_key_for_path_images(message: Message | CallbackQuery) -> str:
        return f'redis_key_for_images:{message.from_user.id}'

    @staticmethod
    async def __redis_key_for_delete_image() -> str:
        secret_key = uuid4()
        return str(secret_key)

    async def delete_redis_key_for_images(self, message: Message | CallbackQuery, storage: RedisStorage):
        redis_key_for_path = await self.__redis_key_for_path_images(message=message)
        redis_key_for_delete_image = await self.__redis_key_for_delete_image()
        return await storage.redis.delete(redis_key_for_path, redis_key_for_delete_image)

    @staticmethod
    async def __replace_value(key: str, storage: RedisStorage) -> str:
        value = await storage.redis.get(key)
        return str(value).replace("b'", '').replace("'", '')

    @staticmethod
    async def __get_file_id(message: Message | CallbackQuery, bot: Bot) -> str:
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        return file_info.file_id

    async def get_redis_value(self, message: Message | CallbackQuery,  storage: RedisStorage) -> str:
        key = await self.__redis_key_for_path_images(message=message)
        return await self.__replace_value(key=key, storage=storage)

    async def save_image_in_redis(
            self,
            message: Message | CallbackQuery,
            bot: Bot,
            storage: RedisStorage,
    ) -> str:
        key = await self.__redis_key_for_path_images(message=message)
        file_id = await self.__get_file_id(message=message, bot=bot)

        await storage.redis.set(key, file_id)

        return await self.__replace_value(key=key, storage=storage)

    async def public_image(
            self,
            message: Message | CallbackQuery,
            storage: RedisStorage,
            is_test: bool = False
    ):
        key = await self.__redis_key_for_path_images(message=message)
        file_id = await self.__replace_value(key=key, storage=storage)

        if is_test:
            return file_id

        return await self.delete_redis_key_for_images(message=message, storage=storage)


static = Static()
