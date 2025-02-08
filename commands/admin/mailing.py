import logging
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.exceptions import TelegramForbiddenError

from database import get_all_users

from dotenv import load_dotenv
import os

load_dotenv(override=True)

TELEGRAM_ID_ADMIN = int(os.getenv("TELEGRAM_ID_ADMIN"))

def register_mailing(dp: Dispatcher):
    @dp.message(Command("mailing"))
    async def mailing_handler(message: Message):
        """Команда для рассылки сообщений всем пользователям"""
        if message.from_user.id != TELEGRAM_ID_ADMIN:
            logging.error(
                f"ВНИМАНИЕ! Неавторизованный пользователь {message.from_user.full_name} ({message.from_user.id}) попытался использовать /mailing"
            )
            return

        if message.chat.type != "private":
            await message.answer("🚫 Эта команда доступна только в личных сообщениях с ботом.")
            return

        text = message.text[len("/mailing "):].strip()
        if not text:
            await message.answer("❌ Пожалуйста, укажите текст для рассылки.")
            return

        users = await get_all_users()

        if not users:
            await message.answer("⚠️ В базе данных нет пользователей для рассылки.")
            return

        success_count = 0
        fail_count = 0

        for user_id, username, full_name in users:
            try:
                await message.bot.send_message(chat_id=user_id, text=text)
                success_count += 1
            except TelegramForbiddenError:
                logging.warning(f"⚠️ Не удалось отправить сообщение пользователю {full_name} ({user_id}). Возможно, он заблокировал бота.")
                fail_count += 1

        await message.answer(
            f"✅ Рассылка завершена!\n\n"
            f"Отправлено: {success_count} пользователям.\n"
            f"Не доставлено: {fail_count} пользователям (возможно, заблокировали бота)."
        )
