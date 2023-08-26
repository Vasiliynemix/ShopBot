from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Product, Category
from src.db.repositories.abstract import Repository


class ProductRepo(Repository[Product]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Product, session=session)

    async def new(
            self,
            name: str,
            description: str,
            price: float,
            category: Category
    ) -> Product:
        await self.session.merge(Product(
            name=name, description=description, price=price, category=Category(category_name=category))
        )
        await self.session.commit()
        product_id = await self.__get_product_by_name(name=name)
        return product_id

    async def __get_product_by_name(self, name: str):
        product_id = await self.session.scalar(
            select(Product.id).where(Product.name == name).limit(1)
        )
        return product_id

    async def get_products(self, category_name: str):
        products = await self.session.scalars(
            select(Product).where(Product.category.has(category_name=category_name))
        )
        return products.all()
