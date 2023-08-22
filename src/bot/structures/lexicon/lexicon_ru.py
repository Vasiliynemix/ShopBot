from dataclasses import dataclass

from aiogram import Bot

from src.bot.structures.keyboards.main_menu import set_main_menu

LEXICON_COMMANDS_ADMIN: dict[str, str] = {
    '/moderators': 'Список админов и модераторов',
    '/admin': 'Добавление админов группы',
    '/start': 'Перезагрузка бота',
}
LEXICON_COMMANDS_MODERATOR: dict[str, str] = {
    'help': 'Описание команды help',
    '/start': 'Перезагрузка бота',
}
LEXICON_COMMANDS_USER: dict[str, str] = {
    'help': 'Описание команды help',
    '/start': 'Перезагрузка бота',
}


@dataclass
class MainMenu:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def get_menu_user(self):
        await set_main_menu(self.bot, menu=LEXICON_COMMANDS_USER)

    async def get_menu_admin(self):
        await set_main_menu(self.bot, menu=LEXICON_COMMANDS_ADMIN)

    async def get_menu_moderator(self):
        await set_main_menu(self.bot, menu=LEXICON_COMMANDS_MODERATOR)
