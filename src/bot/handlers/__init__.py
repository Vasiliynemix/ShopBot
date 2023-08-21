from .start import router as start_router
from .admin import router as admin_router
from .moderator import router as moderator_router

routers = (
    start_router,
    admin_router,
    moderator_router,
)
