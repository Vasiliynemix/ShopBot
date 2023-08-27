from aiogram import Bot
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Message, CallbackQuery

from src.bot.common.images import static


class UpdateProduct:
    @staticmethod
    async def redis_key_for_update_value(chat_id: int) -> str:
        return f'redis_key_update_value:{chat_id}'

    @staticmethod
    async def __replace_update_value(key: str, storage: RedisStorage) -> str:
        value = await storage.redis.get(key)
        return str(value).replace("b'", '').replace("'", '').replace('update_', '')

    @staticmethod
    async def delete_redis_key_for_update(key: str, storage: RedisStorage):
        return await storage.redis.delete(key)

    async def add_update_value(self, value: str, storage: RedisStorage, chat_id: int):
        key = await self.redis_key_for_update_value(chat_id=chat_id)
        await storage.redis.set(key, value)

        return await self.__replace_update_value(key=key, storage=storage)

    async def get_update_value_in_key(self, chat_id: int, storage: RedisStorage) -> str:
        key = await self.redis_key_for_update_value(chat_id=chat_id)

        return await self.__replace_update_value(key=key, storage=storage)


update_product = UpdateProduct()
