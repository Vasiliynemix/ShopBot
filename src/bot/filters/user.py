from aiogram.filters.callback_data import CallbackData


class CallBackCategoriesListFilter(CallbackData, prefix="category"):
    category_name: str


class ProductMenuFilter(CallbackData, prefix="product_menu"):
    product_name: str
