import logging
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

load_dotenv(override=True)
TOKEN = os.getenv("TELEGRAM_API_KEY")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8")
    ]
)

bot = Bot(token=TOKEN)
dp = Dispatcher()

from commands import start, help as help_module, weather, forecast, info

start.register_start(dp)
help_module.register_help(dp)
weather.register_weather(dp)
forecast.register_forecast(dp)
info.register_info(dp)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
