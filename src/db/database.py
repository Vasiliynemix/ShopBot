from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine

from src.configuration import conf
from src.db.repositories.category import CategoryRepo
from src.db.repositories.product import ProductRepo
from src.db.repositories.user import UserRepo


def create_async_engine(url: URL | str) -> AsyncEngine:
    return _create_async_engine(url=url, echo=conf.debug, pool_pre_ping=True)


class Database:
    def __init__(
            self,
            session: AsyncSession,
            user: UserRepo = None,
            product: ProductRepo = None,
            category: CategoryRepo = None
    ):
        self.session = session
        self.user = user or UserRepo(session=session)
        self.product = product or ProductRepo(session=session)
        self.category = category or CategoryRepo(session=session)
