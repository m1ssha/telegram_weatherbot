import asyncio
import logging
from client import dp, client

async def main():
    logging.info("Бот запущен и готов к работе...")
    await dp.start_polling(client)


if __name__ == "__main__":
    asyncio.run(main())