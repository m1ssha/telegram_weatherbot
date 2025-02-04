import logging
from aiogram import Dispatcher, types
from database import add_user

def register_user_logger(dp: Dispatcher):
    @dp.message()
    async def log_user(message: types.Message):
        """Фиксирует всех пользователей, которые пишут боту"""
        user = message.from_user
        await add_user(user.id, user.username or "No username", user.full_name)
        logging.info(f"Записан новый пользователь: {user.full_name} ({user.id})")
