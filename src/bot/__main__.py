import asyncio
import logging

from aiogram import Bot
from redis.asyncio.client import Redis

from src.bot.dispatcher import get_dispatcher, get_redis_storage
from src.bot.structures.data_structure import TransferData
from src.bot.structures.keyboards.main_menu import set_main_menu
from src.configuration import conf
from src.db.database import create_async_engine


async def start_bot():
    bot = Bot(token=conf.bot.token, parse_mode='HTML')

    await set_main_menu(bot=bot)

    storage = get_redis_storage(
        redis=Redis(
            db=conf.redis.db,
            host=conf.redis.host,
            password=conf.redis.passwd,
            username=conf.redis.username,
            port=conf.redis.port,
        )
    )
    dp = get_dispatcher(storage=storage)

    await dp.start_polling(
        bot,
        allowed_updates=dp.resolve_used_update_types(),
        **TransferData(
            engine=create_async_engine(url=conf.db.build_connection_str())
        )
    )


if __name__ == '__main__':
    try:
        logging.basicConfig(
            level=conf.logging_level,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        )
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")
