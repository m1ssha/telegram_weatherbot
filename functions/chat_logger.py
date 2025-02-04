import logging
from aiogram import Dispatcher, types
from database import add_chat, remove_chat

def register_chat_logger(dp: Dispatcher):
    @dp.my_chat_member()
    async def chat_member_handler(update: types.ChatMemberUpdated):
        """Фиксируем добавление и удаление бота из чатов"""
        chat = update.chat
        status = update.new_chat_member.status

        if status in ["member", "administrator"]:  # Бот добавлен в чат
            await add_chat(chat.id, chat.title or "Без названия")
            logging.info(f"Бот добавлен в чат: {chat.title} ({chat.id})")
        elif status == "kicked":  # Бот удален из чата
            await remove_chat(chat.id)
            logging.info(f"Бот удалён из чата: {chat.title} ({chat.id})")
