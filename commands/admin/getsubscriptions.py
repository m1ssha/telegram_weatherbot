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


def register_getsubscriptions(dp: Dispatcher):
    """Регистрирует команду /getsubscriptions для администраторов"""
    @dp.message(Command("getsubscriptions"))
    async def getsubscriptions_handler(message: Message):
        if message.from_user.id != TELEGRAM_ID_ADMIN:
            logging.error(f"ВНИМАНИЕ! Пользователь {message.from_user.full_name} ({message.from_user.id}) вызвал команду /getsubscriptions")
            return
        
        if message.chat.type != "private":
            await message.answer("🚫 Эта команда доступна только в личных сообщениях с ботом.")
            return

        subscriptions = await get_all_subscriptions()

        if not subscriptions:
            await message.answer("📭 В системе пока нет подписок.")
            return

        response = "<b>Все активные подписки:</b>\n---\n"
        for user_id, city, notify_time in subscriptions:
            response += f"👤 <b>User ID:</b> {user_id}\n📍 <b>Город:</b> {city}\n⏰ <b>Время:</b> {notify_time}\n---\n"

        await message.answer(response, parse_mode="HTML")
