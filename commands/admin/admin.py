import logging
from aiogram import Dispatcher
from aiogram.filters.command import Command
from aiogram.types import Message

from dotenv import load_dotenv
import os

load_dotenv(override=True)

TELEGRAM_ID_ADMIN = int(os.getenv("TELEGRAM_ID_ADMIN"))

def register_admin(dp: Dispatcher):
    @dp.message(Command("admin"))
    async def admin_handler(message: Message):
        if message.from_user.id != TELEGRAM_ID_ADMIN:
            logging.error(
                f"ВНИМАНИЕ! Пользователь {message.from_user.full_name} ({message.from_user.id}) вызвал команду /admin"
            )
            return
        
        if message.chat.type != "private":
            await message.answer("🚫 Эта команда доступна только в личных сообщениях с ботом.")
            return
        
        admin_message = (f"<b>Команды администратора:</b>"
                         f"\n\n<b>/addsubscriptiontouser</b> - добавить пользователю подписку на погоду по его ID в Telegram"
                         f"\n<b>/getsubscriptions</b> - посмотреть все подписки")
        await message.answer(admin_message, parse_mode="HTML")