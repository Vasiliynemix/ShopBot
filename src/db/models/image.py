import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.db.models import Base


class Image(Base):
    file_id: Mapped[str] = mapped_column(primary_key=True)
    product_fk: Mapped[int] = mapped_column(sa.ForeignKey('product.id'))
    product: Mapped['Product'] = relationship(back_populates='image', uselist=False)
