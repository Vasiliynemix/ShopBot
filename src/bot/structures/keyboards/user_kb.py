from aiogram.types import ReplyKeyboardMarkup


async def create_main_user_kb() -> ReplyKeyboardMarkup:
    from aiogram.utils.keyboard import ReplyKeyboardBuilder
    kb = ReplyKeyboardBuilder()
    kb.button(text='Меню')
    kb.button(text='Корзина')
    kb.button(text='Помощь')
    kb.button(text='Поддержка')
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
