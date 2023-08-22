from aiogram import Bot
from aiogram.types import BotCommand

from src.bot.structures.role import Role


async def set_main_menu(bot: Bot, menu: dict[str, str]):
    main_menu_commands = [BotCommand(
        command=command,
        description=description
    ) for command, description in menu.items()]

    await bot.set_my_commands(main_menu_commands)
