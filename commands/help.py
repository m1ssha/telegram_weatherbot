import logging
from aiogram import types
from aiogram.filters import Command
from aiogram.types import Message

from messages import messages

def register_help(dp):
    @dp.message(Command("help"))
    async def help_handler(message: Message):
        logging.info(f"Пользователь {message.from_user.full_name} ({message.from_user.id}) вызвал команду /help")
        answer = messages.help_menu_text
        await message.answer(answer, parse_mode="HTML")
