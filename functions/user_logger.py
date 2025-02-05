from aiogram import Dispatcher, types
from database import add_user

def register_user_logger(dp: Dispatcher):
    @dp.message()
    async def log_user_interaction(message: types.Message):
        user = message.from_user
        await add_user(user.id, user.username or "No username", user.full_name)