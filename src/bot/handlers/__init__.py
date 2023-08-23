from .start import router as start_router
from .help import router as help_router
from .admin import router as admin_router
from .moderator import router as moderator_router
from .user import router as user_router

routers = (
    start_router,
    help_router,
    admin_router,
    moderator_router,
    user_router,
)
