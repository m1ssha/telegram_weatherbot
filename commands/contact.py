import logging
import os
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

load_dotenv(override=True)
TELEGRAM_ID_ADMIN = int(os.getenv("TELEGRAM_ID_ADMIN"))

class ContactForm(StatesGroup):
    waiting_for_message = State()

def register_contact(dp):
    @dp.message(Command("contact"))
    async def contact_handler(message: types.Message, state: FSMContext):
        """Обработчик команды /contact"""
        logging.info(f"Пользователь {message.from_user.full_name} ({message.from_user.id}) вызвал команду /contact")
        await message.answer("Напишите ваше сообщение для администратора")
        await state.set_state(ContactForm.waiting_for_message)

    @dp.message(ContactForm.waiting_for_message)
    async def forward_to_admin(message: types.Message, state: FSMContext):
        """Пересылаем сообщение администратору"""
        if TELEGRAM_ID_ADMIN:
            logging.info(f"Пользователь {message.from_user.full_name} ({message.from_user.id}) отправил сообщение админу.")
            await message.bot.send_message(
                TELEGRAM_ID_ADMIN,
                f"📩 Сообщение от @{message.from_user.username or message.from_user.full_name} (<code>{message.from_user.id}</code>):\n\n{message.text}", parse_mode="HTML"
            )
            await message.answer("✅ Ваше сообщение отправлено администратору.")
        else:
            logging.error("Ошибка: не найден ID администратора.")
            await message.answer("❌ Ошибка: администратор недоступен.")

        await state.clear()
