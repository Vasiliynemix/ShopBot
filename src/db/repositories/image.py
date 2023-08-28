from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Image
from src.db.repositories.abstract import Repository


class ImageRepo(Repository[Image]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Image, session=session)

    async def new(
            self,
            file_id: str
    ) -> None:
        await self.session.merge(
            Image(
                file_id=file_id,
            )
        )

    async def get_file_id(self, file_id: str):
        file_id = await self.session.scalar(
            select(Image.file_id).where(Image.file_id == file_id).limit(1)
        )
        return file_id

    async def get_by_product_fk(self, product_fk: str):
        file_id = await self.session.scalar(
            select(Image.file_id).where(Image.product_fk == product_fk).limit(1)
        )
        return file_id
