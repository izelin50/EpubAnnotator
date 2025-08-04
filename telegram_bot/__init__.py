from .bot import bot, dp
from .handlers import router
from .database import init_db

def setup():
    dp.include_router(router)
    init_db()
