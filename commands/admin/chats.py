import logging
import os
from aiogram import Dispatcher
from aiogram.filters.command import Command
from aiogram.types import Message
from database import get_all_chats
from dotenv import load_dotenv

load_dotenv(override=True)

TELEGRAM_ID_ADMIN = int(os.getenv("TELEGRAM_ID_ADMIN"))

def register_chats(dp: Dispatcher):
    @dp.message(Command("chats"))
    async def chats_handler(message: Message):
        if message.from_user.id != TELEGRAM_ID_ADMIN:
            logging.warning(
                f"Несанкционированный доступ к /chats: {message.from_user.full_name} ({message.from_user.id})"
            )
            return
        
        chats = await get_all_chats()
        if not chats:
            await message.answer("⚠️ В базе данных пока нет чатов.")
            return
        
        chat_list = "\n".join([f"🆔 {chat_id} - {chat_title}" for chat_id, chat_title in chats])
        response = f"<b>📋 Список чатов:</b>\n\n{chat_list}"

        await message.answer(response, parse_mode="HTML")
        logging.info(f"Админ {message.from_user.full_name} ({message.from_user.id}) запросил список чатов.")
