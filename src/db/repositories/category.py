from sqlalchemy import select, ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Category
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

    async def get_categories(self) -> ScalarResult[Category]:
        return await self.session.scalars(select(Category).distinct(Category.category_name))

    async def get_one_category(self, category_name: str) -> int:
        category_id = await self.session.scalar(
            select(Category.id).where(Category.category_name == category_name).limit(1)
        )
        return category_id
