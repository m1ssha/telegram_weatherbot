import logging
import os
import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from commands import start, help as help_module, weather, forecast, info, subscribe, mysubscriptions, unsubscribe, contact
from functions import chat_logger, user_logger
from commands.admin import getsubscriptions, addsubscriptiontouser, admin, answer, chats, users, removesubscription

import database

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
contact.register_contact(dp)

subscribe.register_subscribe(dp)
mysubscriptions.register_mysubscriptions(dp)
unsubscribe.register_unsubscribe(dp)

getsubscriptions.register_getsubscriptions(dp)
addsubscriptiontouser.register_addsubscriptiontouser(dp)
removesubscription.register_removesubscriptiontouser(dp)
admin.register_admin(dp)
answer.register_answer(dp)
chats.register_chats(dp)
users.register_users(dp)

async def main():
    """Основная функция для запуска бота"""
    await database.init_db()
    chat_logger.register_chat_logger(dp)
    user_logger.register_user_logger(dp)
    await subscribe.init_db()
    subscribe.schedule_daily_forecasts(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
