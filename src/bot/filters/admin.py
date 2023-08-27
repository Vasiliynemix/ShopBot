from aiogram.filters.callback_data import CallbackData


class CallBackAdminListFilter(CallbackData, prefix="moderator"):
    admin_id: int


class CallBackRequestStatusModeratorFilter(CallbackData, prefix="request_status_moderator"):
    user_id: str
