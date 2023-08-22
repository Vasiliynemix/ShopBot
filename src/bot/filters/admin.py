from aiogram.filters.callback_data import CallbackData


class CallBackAdminListFilter(CallbackData, prefix="moderator"):
    admin_id: int
