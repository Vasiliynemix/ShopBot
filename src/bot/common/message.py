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
    async def __replace_redis_value(value) -> str:
        return str(value).replace("b'", '').replace("'", '')

    async def get_value_in_key(self, chat_id: int, storage: RedisStorage):
        key = await self.__redis_key_for_message_id(chat_id=chat_id)
        return set(await storage.redis.lrange(key, 0, -1))

    async def delete_message(self, chat_id: int, message_ids_list: list[int], bot: Bot, storage: RedisStorage):
        key = await self.__redis_key_for_message_id(chat_id=chat_id)
        for message_id in message_ids_list:
            replace_value = int(await self.__replace_redis_value(value=message_id))
            await self.delete_redis_key_for_message(key=key, storage=storage)
            await bot.delete_message(chat_id=chat_id, message_id=replace_value)

    async def add_message_id_in_redis(self, chat_id: int, message_ids_list: list[int], storage: RedisStorage):
        key = await self.__redis_key_for_message_id(chat_id=chat_id)
        for message_id in message_ids_list:
            await storage.redis.rpush(key, message_id)

        return set(await storage.redis.lrange(key, 0, -1))


change_message = ChangeMessage()
