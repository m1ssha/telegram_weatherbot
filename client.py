import logging
import os
import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from commands import start, help as help_module, weather, forecast, info, subscribe, mysubscriptions, unsubscribe
from commands.admin import getsubscriptions, addsubscriptiontouser
# from commands.keyboard.user_keyboard import user_keyboard

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


start.register_start(dp)
help_module.register_help(dp)
weather.register_weather(dp)
forecast.register_forecast(dp)
info.register_info(dp)
subscribe.register_subscribe(dp)
mysubscriptions.register_mysubscriptions(dp)
unsubscribe.register_unsubscribe(dp)
getsubscriptions.register_getsubscriptions(dp)
addsubscriptiontouser.register_addsubscriptiontouser(dp)


async def main():
    """Основная функция для запуска бота"""
    await subscribe.init_db()
    subscribe.schedule_daily_forecasts(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
