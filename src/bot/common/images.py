import os
from typing import Any

from aiogram import Bot
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Message, CallbackQuery, InputMediaPhoto


class Static:
    def __init__(self):
        self.path_to_static = '../../static'

    @staticmethod
    async def __is_exists_dir(path: str):
        if not os.path.exists(path):
            os.mkdir(path)

    async def __create_static_if_not_exists(self):
        await self.__is_exists_dir(path=self.path_to_static)

    async def __create_category_if_not_exists(self, category_id: int) -> str:
        path_to_category = f'{self.path_to_static}/category_{category_id}'
        await self.__is_exists_dir(path=path_to_category)
        return path_to_category

    async def __create_product_dir_if_not_exists(self, category_id: int, product_id: int):
        await self.__create_static_if_not_exists()
        path_to_category = await self.__create_category_if_not_exists(category_id=category_id)
        path_to_product = f'{path_to_category}/product_{product_id}'
        await self.__is_exists_dir(path=path_to_product)
        return path_to_product

    @staticmethod
    async def __redis_key_for_path_images(message: Message | CallbackQuery) -> str:
        return f'redis_key_for_images{message.from_user.id}'

    async def __delete_product_images(self, image_path: str):
        items = await self.__get_images_dir(image_path=image_path)
        for item in items:
            item_path = os.path.join(image_path, item)

            if os.path.isfile(item_path):
                os.remove(item_path)

    @staticmethod
    async def __get_images_dir(image_path: str) -> list[str]:
        return os.listdir(image_path)

    async def save_images_in_redis(
            self,
            message: Message | CallbackQuery,
            bot: Bot,
            storage: RedisStorage,
    ):
        redis_key = await self.__redis_key_for_path_images(message=message)
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        file_path = file_info.file_path
        await storage.redis.rpush(redis_key, file_path)
        return set(await storage.redis.lrange(redis_key, 0, -1))

    async def save_images(
            self,
            message: Message | CallbackQuery,
            storage: RedisStorage,
            bot: Bot,
            category_id: int = 1,
            product_id: int = 1,
            is_test: bool = False,
    ) -> list[InputMediaPhoto] | None:
        redis_key = await self.__redis_key_for_path_images(message=message)
        path_list = set(await storage.redis.lrange(redis_key, 0, -1))

        image_path = await self.__create_product_dir_if_not_exists(category_id=category_id, product_id=product_id)

        items = os.listdir(image_path)
        files = [item for item in items if os.path.isfile(os.path.join(image_path, item))]

        count_files = len(files) + 1

        for i, path in enumerate(path_list):
            _path = str(path).replace("b'", '').replace("'", '')
            downloaded_file = await bot.download_file(_path)
            with open(f'{image_path}/{i + count_files}.jpg', "wb") as img_file:
                img_file.write(downloaded_file.read())

        if is_test:
            images = await self.public_images(category_id=category_id, product_id=product_id)
            await self.__delete_product_images(image_path=image_path)
            return images
        await storage.redis.delete(redis_key)

    async def public_images(self, category_id: int, product_id: int) -> list[InputMediaPhoto]:
        image_path = await self.__create_product_dir_if_not_exists(category_id=category_id, product_id=product_id)
        items = await self.__get_images_dir(image_path=image_path)
        images = []
        for _ in items:
            images.append(InputMediaPhoto(media=image_path))
        return images


static = Static()
