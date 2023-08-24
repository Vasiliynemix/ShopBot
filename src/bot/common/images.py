import os


class Static:
    def __init__(self):
        self.path = '../../static'

    async def __create_static_if_not_exists(self):
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    async def __create_category_if_not_exists(self, category_id: int) -> str:
        path = f'{self.path}/category_{category_id}'
        if not os.path.exists(f'{self.path}/category_{category_id}'):
            os.mkdir(f'{self.path}/category_{category_id}')
        return path

    async def create_product_dir_if_not_exists(self, category_id: int, product_id: int):
        await self.__create_static_if_not_exists()
        path_to_category = await self.__create_category_if_not_exists(category_id=category_id)
        path = f'{path_to_category}/product_{product_id}'
        if not os.path.exists(path):
            os.mkdir(path)
        return path


static = Static()
