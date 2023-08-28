from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Product, Category, Image
from src.db.repositories.abstract import Repository


class ProductRepo(Repository[Product]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Product, session=session)

    async def new(
            self,
            name: str,
            description: str,
            price: float,
            volume: int,
            category: Category,
            image: Image
    ) -> Product:
        await self.session.merge(Product(
            name=name,
            description=description,
            price=price,
            volume=volume,
            category=Category(category_name=category),
            image=Image(file_id=image)
        )
        )
        await self.session.commit()
        return await self.__get_product_by_name(name=name)

    async def __get_product_by_name(self, name: str):
        product = await self.session.scalar(
            select(Product).where(Product.name == name).limit(1)
        )
        return product

    async def get_products(self, category_name: str):
        products = await self.session.scalars(
            select(Product).where(Product.category.has(category_name=category_name))
        )
        return products.all()

    async def get_product_name(self, product_name: str):
        product_name = await self.session.scalar(
            select(Product).where(Product.name == product_name)
        )
        return product_name
