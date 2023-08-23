from typing import List

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models import Base


class Category(Base):
    category_name: Mapped[str] = mapped_column(sa.Text, primary_key=True)
    product_fk: Mapped[int] = mapped_column(sa.ForeignKey('product.id'))
    products: Mapped[List['Product']] = relationship(back_populates='category', uselist=True)
