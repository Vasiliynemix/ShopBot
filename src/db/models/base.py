from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    @classmethod
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __allow_unmapped__ = False

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
