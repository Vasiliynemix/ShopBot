from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine

from src.configuration import conf
from src.db.repositories.user import UserRepo


def create_async_engine(url: URL | str) -> AsyncEngine:
    return _create_async_engine(url=url, echo=conf.debug, pool_pre_ping=True)


class Database:
    def __init__(
            self,
            session: AsyncSession,
            user: UserRepo = None,
    ):
        self.session = session
        self.user = user or UserRepo(session=session)
