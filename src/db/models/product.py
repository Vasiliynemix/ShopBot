import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models import Base


class Product(Base):
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    description: Mapped[str]
    price: Mapped[float]
    volume: Mapped[int] = mapped_column(default=0)

    category: Mapped['Category'] = relationship(back_populates='products', uselist=False)
    image: Mapped['Image'] = relationship(back_populates='product', uselist=False)
