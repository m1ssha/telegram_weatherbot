import aiosqlite
from aiogram import Dispatcher
from aiogram.filters.command import Command
from aiogram.types import Message

from messages import messages

DB_FILE = "subscriptions.db"

async def get_user_subscriptions(user_id: int):
    """Получает подписки конкретного пользователя."""
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT city, notify_time FROM subscriptions WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchall()


def register_mysubscriptions(dp: Dispatcher):
    """Регистрирует команду /mysubscriptions."""
    @dp.message(Command("mysubscriptions"))
    async def my_subscriptions_handler(message: Message):
        if message.chat.type != "private":
            await message.answer("🚫 Эта команда доступна только в личных сообщениях с ботом.")
            return
        
        subscriptions = await get_user_subscriptions(message.from_user.id)
        
        if not subscriptions:
            await message.answer("❌ У вас нет активных подписок.")
            return

        answer = messages.info_mysubscriptions
        for city, notify_time in subscriptions:
            answer += f"📍 <b>{city}</b> — ⏰ {notify_time}\n"

        await message.answer(answer, parse_mode="HTML")
