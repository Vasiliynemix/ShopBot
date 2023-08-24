import logging
import os
from dataclasses import dataclass
from dotenv import load_dotenv

from sqlalchemy.engine import URL

from src.bot.common.images import Static

load_dotenv()


@dataclass
class DatabaseConfig:
    name: str | None = os.getenv('DB_NAME')
    user: str | None = os.getenv('DB_USERNAME')
    passwd: str | None = os.getenv('DB_PASSWORD', None)
    port: int = int(os.getenv('DB_PORT', 5432))
    host: str = os.getenv('DB_HOST', 'db')

    driver: str = os.getenv('DRIVER')
    database_system: str = os.getenv('DATABASE_SYSTEM')

    def build_connection_str(self) -> str:
        return URL.create(
            drivername=f'{self.database_system}+{self.driver}',
            username=self.user,
            database=self.name,
            password=self.passwd,
            port=self.port,
            host=self.host,
        ).render_as_string(hide_password=False)


@dataclass
class RedisConfig:
    db: int = int(os.getenv('REDIS_DATABASE', 1))
    """ Redis Database ID """
    host: str = os.getenv('REDIS_HOST', 'redis')
    port: int = int(os.getenv('REDIS_PORT', 6379))
    passwd: str | None = os.getenv('REDIS_PASSWORD')
    username: str | None = os.getenv('REDIS_USERNAME')
    state_ttl: int | None = os.getenv('REDIS_TTL_STATE', None)
    data_ttl: int | None = os.getenv('REDIS_TTL_DATA', None)


@dataclass
class BotConfig:
    token: str = os.getenv('BOT_TOKEN')


@dataclass
class AdminConfig:
    admin_id: int = int(os.getenv('SUPER_ADMIN_ID'))


@dataclass
class Configuration:
    debug = bool(os.getenv('DEBUG'))
    logging_level = int(os.getenv('LOGGING_LEVEL', logging.INFO))

    db = DatabaseConfig()
    redis = RedisConfig()
    bot = BotConfig()
    admin = AdminConfig()


conf = Configuration()
