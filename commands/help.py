import logging
from aiogram import types
from aiogram.filters import Command
from aiogram.types import Message

from messages import messages

def register_help(dp):
    @dp.message(Command("help"))
    async def help_handler(message: Message):
        logging.info(f"Пользователь {message.from_user.full_name} ({message.from_user.id}) вызвал команду /help")
        # answer = (
        #     "📌 <b>Меню помощи</b> 📌\n\n"
        #     "<b>/weather [город]</b> - Получает текущую погоду в указанном городе.\n"
        #     "  🔹 <i>Пример:</i> <code>/weather Москва</code>\n\n"
        #     "<b>/forecast [город] [часы/дни]</b> - Прогноз погоды на указанное время.\n"
        #     "По умолчанию выводится прогноз погоды на ближайшие 6 часов\n"
        #     "  🔹 <i>Пример:</i> <code>/forecast Москва 12</code> (на 12 часов)\n"
        #     "  🔹 <i>Пример:</i> <code>/forecast Москва 48</code> (на 2 дня)\n\n"
        #     "<b>/info [город]</b> - Выводит информацию о городе\n\n"
        #     "💡 Бот использует данные OpenWeatherMap 🌍"
        # )
        answer = messages.help_menu_text
        await message.answer(answer, parse_mode="HTML")
