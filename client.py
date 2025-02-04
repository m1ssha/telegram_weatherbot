import logging
import os
import asyncio
import importlib
import pkgutil
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

import database
from functions import chat_logger, user_logger

load_dotenv(override=True)
TOKEN = os.getenv("TELEGRAM_API_KEY")

LOG_FILE = "bot.log"
LOG_MAX_SIZE_MB = 100

def clear_old_logs():
    if os.path.exists(LOG_FILE):
        file_size_mb = os.path.getsize(LOG_FILE) / (1024 * 1024)
        if file_size_mb > LOG_MAX_SIZE_MB:
            os.remove(LOG_FILE)
            print(f"🗑 Лог-файл {LOG_FILE} был удален (размер {file_size_mb:.2f} MB > {LOG_MAX_SIZE_MB} MB)")

clear_old_logs()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ]
)


bot = Bot(token=TOKEN)
dp = Dispatcher()


def auto_register_commands(dp: Dispatcher, package: str):
    package_path = package.replace(".", "/")
    for _, module_name, _ in pkgutil.iter_modules([package_path]):
        module = importlib.import_module(f"{package}.{module_name}")
        register_function_name = f"register_{module_name}"
        
        if hasattr(module, register_function_name):
            getattr(module, register_function_name)(dp)
            logging.info(f"✅ Зарегистрирована команда: {module_name}")


auto_register_commands(dp, "commands")
auto_register_commands(dp, "commands.admin")


async def main():
    await database.init_db()
    chat_logger.register_chat_logger(dp)
    user_logger.register_user_logger(dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
