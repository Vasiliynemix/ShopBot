from aiogram import Bot
from aiogram.fsm.storage.redis import RedisStorage


class ChangeMessage:
    @staticmethod
    async def __redis_key_for_message_id(chat_id: int) -> str:
        return f'redis_key_message_id:{chat_id}'

    @staticmethod
    async def delete_redis_key_for_message(key: str, storage: RedisStorage):
        return await storage.redis.delete(key)

    @staticmethod
    async def __replace_value(key: str, storage: RedisStorage) -> str:
        value = await storage.redis.get(key)
        return str(value).replace("b'", '').replace("'", '')

    async def get_value_in_key(self, chat_id: int, storage: RedisStorage):
        key = await self.__redis_key_for_message_id(chat_id=chat_id)

        return await self.__replace_value(key=key, storage=storage)

    async def delete_message(self, chat_id: int, message_id: int, bot: Bot, storage: RedisStorage):
        key = await self.__redis_key_for_message_id(chat_id=chat_id)
        await self.delete_redis_key_for_message(key=key, storage=storage)

        return await bot.delete_message(chat_id=chat_id, message_id=message_id)

    async def add_message_id_in_redis(self, chat_id: int, message_id: int, storage: RedisStorage):
        key = await self.__redis_key_for_message_id(chat_id=chat_id)
        await storage.redis.set(key, message_id)

        return await self.__replace_value(key=key, storage=storage)


change_message = ChangeMessage()
