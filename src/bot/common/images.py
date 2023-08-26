from uuid import uuid4

from aiogram import Bot, types
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Message, CallbackQuery

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
    async def __replace_redis_key(redis_key: str) -> str:
        return str(redis_key).replace("b'", '').replace("'", '')

    async def save_images_in_redis(
            self,
            message: Message | CallbackQuery,
            bot: Bot,
            storage: RedisStorage,
    ):
        redis_key = await self.__redis_key_for_path_images(message=message)
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        file_id = file_info.file_id
        await storage.redis.rpush(redis_key, file_id)
        return set(await storage.redis.lrange(redis_key, 0, -1))

    async def test_answer_images(
            self,
            message: Message | CallbackQuery,
            storage: RedisStorage,
            product_data: dict,
            is_test: bool = False,
    ):
        redis_key = await self.__redis_key_for_path_images(message=message)
        path_photo_list = set(await storage.redis.lrange(redis_key, 0, -1))

        if is_test:
            media_data = []

            for photo_path in path_photo_list:
                url = await self.__replace_redis_key(redis_key=photo_path)
                caption = await create_text_product(
                    name=product_data['name'],
                    description=product_data['description'],
                    price=product_data['price'],
                    category=product_data['category'],
                )
                media = types.InputMediaPhoto(media=url, caption=caption)
                media_data.append(media)

            return media_data

        return await self.delete_redis_key_for_images(message=message, storage=storage)

    async def public_images(self, category_name: str, product_id: int):
        # image_path = await self.__create_product_dir_if_not_exists(category_name=category_name, product_id=product_id)
        # await self.__update_folder_google_drive(self.folder_id, self.path_to_static)
        # items = await self.__get_images_dir(image_path=image_path)
        # images = []
        # for _ in items:
        #     images.append(InputMediaPhoto(media=image_path))
        # return images
        pass


static = Static()
