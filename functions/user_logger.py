import logging
from aiogram import Dispatcher, types
from aiogram.filters import Command
from database import add_user

def register_user_logger(dp: Dispatcher):
    @dp.message()
    async def log_user_message(message: types.Message):
        user = message.from_user
        await add_user(user.id, user.username or "No username", user.full_name)

    @dp.message(Command())
    async def log_user_command(message: types.Message):
        user = message.from_user
        await add_user(user.id, user.username or "No username", user.full_name)
