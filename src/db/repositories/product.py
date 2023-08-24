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
        new_product = await self.session.merge(Product(
            name=name, description=description, price=price, category=Category(category_name=category))
        )
        await self.session.commit()
        return new_product.id
