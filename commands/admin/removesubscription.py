import aiosqlite
import logging
import re
from aiogram import Dispatcher
from aiogram.filters.command import Command
from aiogram.types import Message

from dotenv import load_dotenv
import os

load_dotenv(override=True)

TELEGRAM_ID_ADMIN = int(os.getenv("TELEGRAM_ID_ADMIN"))

DB_FILE = "subscriptions.db"


async def remove_subscription(user_id: int, city: str, notify_time: str):
    """Удаляет подписку пользователя на определённый город и время."""
    try:
        async with aiosqlite.connect(DB_FILE) as db:
            async with db.execute("SELECT COUNT(*) FROM subscriptions WHERE user_id = ? AND city = ? AND notify_time = ?", 
                                  (user_id, city, notify_time)) as cursor:
                result = await cursor.fetchone()
                if result[0] == 0:
                    return False

            await db.execute("DELETE FROM subscriptions WHERE user_id = ? AND city = ? AND notify_time = ?", 
                             (user_id, city, notify_time))
            await db.commit()
            return True

    except Exception as e:
        logging.error(f"Ошибка при удалении подписки: {e}")
        return False


def register_removesubscriptiontouser(dp: Dispatcher):
    """Регистрирует команду /removesubscriptiontouser для администраторов"""
    @dp.message(Command("removesubscriptiontouser"))
    async def removesubscriptiontouser_handler(message: Message):
        if message.from_user.id != TELEGRAM_ID_ADMIN:
            logging.error(
                f"ВНИМАНИЕ! Пользователь {message.from_user.full_name} ({message.from_user.id}) вызвал команду /removesubscriptiontouser"
            )
            return

        if message.chat.type != "private":
            await message.answer("🚫 Эта команда доступна только в личных сообщениях с ботом.")
            return

        args = message.text.split(maxsplit=3)
        if len(args) < 4:
            await message.answer("❌ Использование: /removesubscriptiontouser <user_id> <city> <notify_time>\nПример: `/removesubscriptiontouser 123456789 Москва 08:00`")
            return

        try:
            user_id = int(args[1])
            city = args[2]
            notify_time = args[3]

            if not re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", notify_time):
                await message.answer("❌ Ошибка: время должно быть в формате ЧЧ:ММ.\nПример: `/removesubscriptiontouser 123456789 Москва 08:00`")
                return

            success = await remove_subscription(user_id, city, notify_time)
            if success:
                await message.answer(f"✅ Подписка на {city} в {notify_time} для пользователя {user_id} успешно удалена.")
            else:
                await message.answer(f"⚠️ Подписка на {city} в {notify_time} у пользователя {user_id} не найдена.")

        except ValueError:
            await message.answer("❌ Ошибка: user_id должен быть числом.\nПример: `/removesubscriptiontouser 123456789 Москва 08:00`")
