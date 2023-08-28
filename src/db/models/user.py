import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from src.bot.structures.role import Role
from src.db.models import Base


class User(Base):
    user_id: Mapped[int] = mapped_column(sa.BigInteger, unique=True, nullable=False)
    """ Telegram user id """
    user_name: Mapped[str] = mapped_column(sa.Text, unique=False, nullable=True)
    """ Telegram user name """
    first_name: Mapped[str] = mapped_column(sa.Text, unique=False, nullable=True)
    """ Telegram profile first name """
    second_name: Mapped[str] = mapped_column(sa.Text, unique=False, nullable=True)
    """ Telegram profile second name """
    language_code: Mapped[str] = mapped_column(sa.Text, unique=False, nullable=True)
    """ Language system Telegram user """
    is_premium: Mapped[bool] = mapped_column(sa.Boolean, unique=False, nullable=False)
    """ Telegram user premium status """

    role: Mapped[Role] = mapped_column(sa.Enum(Role), default=Role.USER)
    request_status_moder: Mapped[int] = mapped_column(nullable=True, default=0)
