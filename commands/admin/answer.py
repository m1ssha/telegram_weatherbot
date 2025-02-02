import logging
import os
from aiogram import Dispatcher
from aiogram.filters.command import CommandObject, Command
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv(override=True)

TELEGRAM_ID_ADMIN = int(os.getenv("TELEGRAM_ID_ADMIN"))

def register_answer(dp: Dispatcher):
    @dp.message(Command("answer"))
    async def answer_handler(message: Message, command: CommandObject):
        """Обработчик команды /answer <user_id> <текст>"""
        if message.from_user.id != TELEGRAM_ID_ADMIN:
            logging.error(
                f"ВНИМАНИЕ! Несанкционированный вызов /answer: {message.from_user.full_name} ({message.from_user.id})"
            )
            return
        
        if message.chat.type != "private":
            await message.answer("🚫 Эта команда доступна только в личных сообщениях с ботом.")
            return

        args = command.args
        if not args:
            await message.answer("❌ Использование: <code>/answer user_id текст сообщения</code>", parse_mode="HTML")
            return

        try:
            user_id, user_message = args.split(" ", 1)
            user_id = int(user_id)
        except ValueError:
            await message.answer("❌ Неверный формат. Используйте: <code>/answer user_id текст</code>", parse_mode="HTML")
            return

        try:
            await message.bot.send_message(user_id, f"📩 Ответ от администратора:\n\n{user_message}")
            await message.answer(f"✅ Сообщение отправлено пользователю <code>{user_id}</code>", parse_mode="HTML")
            logging.info(f"Админ {message.from_user.full_name} ({message.from_user.id}) отправил сообщение пользователю {user_id}")
        except Exception as e:
            logging.error(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
            await message.answer("❌ Ошибка: не удалось отправить сообщение. Возможно, пользователь не писал боту.")
