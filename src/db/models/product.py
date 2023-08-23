import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models import Base


class Product(Base):
    name: Mapped[str]
    description: Mapped[str]
    price: Mapped[float]
    category: Mapped['Category'] = relationship(back_populates='products', uselist=False)
