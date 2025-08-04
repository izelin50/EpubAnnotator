import asyncio
from telegram_bot import bot, dp, setup

async def main():
    setup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
