import logging
from aiogram import types
from aiogram.filters import Command
from aiogram.types import Message

def register_start(dp):
    @dp.message(Command("start"))
    async def start_handler(message: Message):
        logging.info(f"Пользователь {message.from_user.full_name} ({message.from_user.id}) вызвал команду /start")
        answer = (
            f"Привет, {message.from_user.full_name}! Я бот, который подскажет тебе погоду.\n\n"
            f"Вся информация по использованию в /help."
        )
        await message.answer(answer, parse_mode="HTML")
