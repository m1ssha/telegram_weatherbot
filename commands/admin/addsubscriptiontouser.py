import aiosqlite
import logging
from aiogram import Dispatcher
from aiogram.filters.command import Command
from aiogram.types import Message

from dotenv import load_dotenv
import os

load_dotenv(override=True)

TELEGRAM_ID_ADMIN = int(os.getenv("TELEGRAM_ID_ADMIN"))

DB_FILE = "subscriptions.db"


async def get_all_subscriptions():
    """Получает список всех подписок в базе данных."""
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT user_id, city, notify_time FROM subscriptions") as cursor:
            return await cursor.fetchall()


async def count_user_subscriptions(user_id: int):
    """Подсчитывает количество подписок пользователя."""
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT COUNT(*) FROM subscriptions WHERE user_id = ?", (user_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0


async def add_subscription(user_id: int, city: str, notify_time: str):
    """Добавляет подписку в базу данных, если их меньше 10."""
    current_count = await count_user_subscriptions(user_id)

    if current_count >= 10:
        return False

    try:
        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute(
                "INSERT INTO subscriptions (user_id, city, notify_time) VALUES (?, ?, ?)",
                (user_id, city, notify_time),
            )
            await db.commit()
        return True

    except Exception as e:
        logging.error(f"Ошибка при добавлении подписки: {e}")
        return False


def register_addsubscriptiontouser(dp: Dispatcher):
    """Регистрирует команду /addsubscriptiontouser для администраторов"""
    @dp.message(Command("addsubscriptiontouser"))
    async def addsubscriptiontouser_handler(message: Message):
        if message.from_user.id != TELEGRAM_ID_ADMIN:
            logging.error(
                f"ВНИМАНИЕ! Пользователь {message.from_user.full_name} ({message.from_user.id}) вызвал команду /addsubscriptiontouser"
            )
            return

        if message.chat.type != "private":
            await message.answer("🚫 Эта команда доступна только в личных сообщениях с ботом.")
            return

        args = message.text.split(maxsplit=3)
        if len(args) < 4:
            await message.answer("❌ Использование: /addsubscriptiontouser <user_id> <city> <notify_time>\nПример: `/addsubscriptiontouser 123456789 Moscow 08:00`")
            return

        try:
            user_id = int(args[1])
            city = args[2]
            notify_time = args[3]

            success = await add_subscription(user_id, city, notify_time)
            if success:
                await message.answer(f"✅ Подписка для пользователя {user_id} на {city} в {notify_time} успешно добавлена.")
            else:
                await message.answer(f"⚠️ Не удалось добавить подписку для {user_id}. Возможно, у него уже 10 подписок.")

        except ValueError:
            await message.answer("❌ Ошибка: user_id должен быть числом.\nПример: `/addsubscriptiontouser 123456789 Москва 08:00`")
