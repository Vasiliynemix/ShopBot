import os

import os
import shutil

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaFileUpload

from aiogram import Bot
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from transliterate import translit


class Static:
    def __init__(self):
        self.path_to_static = '../../static'
        self.service_account_file = '../../.client_secret_key.json'
        self.api_name = 'drive'
        self.api_version = 'v3'
        self.folder_id = '1xwMrgbhWBUx5e8vsMau-JQBqdy7qQ_98'

    def __create_credentials(self):
        return Credentials.from_service_account_file(
            self.service_account_file,
            scopes=['https://www.googleapis.com/auth/drive']
        )

    def __start_service(self):
        return build(
            self.api_name,
            self.api_version,
            credentials=self.__create_credentials()
        )

    async def __update_folder_google_drive(
            self,
            folder_id,
            local_folder_path
    ):
        service = self.__start_service()
        remote_items = {}
        results = service.files().list(q=f"'{folder_id}' in parents", fields="files(id, name)").execute()
        for item in results.get('files', []):
            remote_items[item['name']] = item['id']
        for item in os.listdir(local_folder_path):
            item_path = os.path.join(local_folder_path, item)

            if os.path.isfile(item_path):
                if item in remote_items:
                    media = MediaFileUpload(item_path)
                    service.files().update(fileId=remote_items[item], media_body=media).execute()
                    del remote_items[item]
                else:
                    media = MediaFileUpload(item_path)
                    file_metadata = {
                        'name': item,
                        'parents': [folder_id]
                    }
                    service.files().create(body=file_metadata, media_body=media).execute()

            elif os.path.isdir(item_path):
                if item in remote_items:
                    subfolder_id = remote_items[item]
                    del remote_items[item]
                else:
                    subfolder_metadata = {
                        'name': item,
                        'parents': [folder_id],
                        'mimeType': 'application/vnd.google-apps.folder'
                    }
                    subfolder = service.files().create(body=subfolder_metadata, fields='id').execute()
                    subfolder_id = subfolder.get('id')
                await self.__update_folder_google_drive(subfolder_id, item_path)

        for remote_item in remote_items.values():
            service.files().delete(fileId=remote_item).execute()

    @staticmethod
    async def __is_exists_dir(path: str):
        if not os.path.exists(path):
            os.mkdir(path)

    async def __create_static_if_not_exists(self):
        await self.__is_exists_dir(path=self.path_to_static)

    async def __create_category_if_not_exists(self, category_name: str) -> str:
        transliterated_name = (str(translit(category_name, 'ru', reversed=True)).replace(' ', '_'))
        path_to_category = f'{self.path_to_static}/category_{transliterated_name}'
        await self.__is_exists_dir(path=path_to_category)
        return path_to_category

    async def __create_product_dir_if_not_exists(self, category_name: str, product_id: int):
        await self.__create_static_if_not_exists()
        path_to_category = await self.__create_category_if_not_exists(category_name=category_name)
        path_to_product = f'{path_to_category}/product_{product_id}'
        await self.__is_exists_dir(path=path_to_product)
        return {'path_to_category': path_to_category, 'path_to_product': path_to_product}

    @staticmethod
    async def __redis_key_for_path_images(message: Message | CallbackQuery) -> str:
        return f'redis_key_for_images:{message.from_user.id}'

    @staticmethod
    async def __delete_product_images(image_path: dict[str, str], is_test: bool = False):
        if is_test:
            shutil.rmtree(image_path.get('path_to_category'))
        else:
            shutil.rmtree(image_path.get('path_to_product'))

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
            category_name: str = 'test',
            product_id: int = 1,
            is_test: bool = False,
    ):
        redis_key = await self.__redis_key_for_path_images(message=message)
        path_list = set(await storage.redis.lrange(redis_key, 0, -1))

        image_path = await self.__create_product_dir_if_not_exists(category_name=category_name, product_id=product_id)

        items = os.listdir(image_path.get('path_to_product'))
        files = [item for item in items if os.path.isfile(os.path.join(image_path.get('path_to_product'), item))]

        count_files = len(files) + 1

        for i, path in enumerate(path_list):
            _path = str(path).replace("b'", '').replace("'", '')
            downloaded_file = await bot.download_file(_path)
            with open(f'{image_path.get("path_to_product")}/{i + count_files}.jpg', "wb") as img_file:
                img_file.write(downloaded_file.read())

        if is_test:
            # images = await self.public_images(category_id=category_id, product_id=product_id)
            await self.__delete_product_images(image_path=image_path, is_test=True)
            # return images
            return True
        await storage.redis.delete(redis_key)

    async def public_images(self, category_name: str, product_id: int):
        image_path = await self.__create_product_dir_if_not_exists(category_name=category_name, product_id=product_id)
        await self.__update_folder_google_drive(self.folder_id, self.path_to_static)
        # items = await self.__get_images_dir(image_path=image_path)
        # images = []
        # for _ in items:
        #     images.append(InputMediaPhoto(media=image_path))
        # return images


static = Static()
