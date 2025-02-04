import logging
import os
from aiogram import Dispatcher
from aiogram.filters.command import Command
from aiogram.types import Message
from database import get_all_users
from dotenv import load_dotenv

load_dotenv(override=True)

TELEGRAM_ID_ADMIN = int(os.getenv("TELEGRAM_ID_ADMIN"))

def register_users(dp: Dispatcher):
    @dp.message(Command("users"))
    async def users_handler(message: Message):
        """Вывод списка пользователей для админа"""
        if message.from_user.id != TELEGRAM_ID_ADMIN:
            logging.warning(
                f"Несанкционированный доступ к /users: {message.from_user.full_name} ({message.from_user.id})"
            )
            return
        
        if message.chat.type != "private":
            await message.answer("🚫 Эта команда доступна только в личных сообщениях с ботом.")
            return
        
        users = await get_all_users()
        users_count = len(users)
        if not users:
            await message.answer("⚠️ В базе данных пока нет пользователей.")
            return
        
        user_list = "\n".join([f"🆔 <code>{user_id}</code> - @{username} ({full_name})" for user_id, username, full_name in users])
        response = f"<b>📋 Список пользователей ({users_count}):</b>\n\n{user_list}"

        await message.answer(response, parse_mode="HTML")
        logging.info(f"Админ {message.from_user.full_name} ({message.from_user.id}) запросил список пользователей.")
