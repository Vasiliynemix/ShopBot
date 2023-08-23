from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Product, Category
from src.db.repositories.abstract import Repository


class CategoryRepo(Repository[Category]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Category, session=session)

    async def new(
            self,
            category_name: str,
    ) -> None:
        await self.session.merge(
            Category(
                category_name=category_name,
            )
        )

    async def get_categories(self):
        return await self.session.scalars(select(Category).distinct(Category.category_name))

    async def get_one_category(self, category_name: str):
        return await self.session.scalar(select(Category)
                                         .where(Category.category_name == category_name).limit(1))
