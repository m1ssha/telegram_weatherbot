import re
import logging
from aiogram import types
from aiogram.filters import Command
from aiogram.types import Message
from weather_api import get_city_info

def register_info(dp):
    @dp.message(Command("info"))
    async def city_info_handler(message: Message, command):
        await message.answer("Команда временно не работает.")


# def register_info(dp):
#     @dp.message(Command("info"))
#     async def city_info_handler(message: Message, command):
#         if command.args:
#             city = command.args.strip()

#             if not re.match(r"^[a-zA-Zа-яА-ЯёЁ\s\-]+$", city):
#                 logging.warning(f"Ошибка ввода города: {message.text}")
#                 await message.answer(
#                     "🚫 Ошибка: название города должно содержать только буквы и пробелы. Пример: <code>/weather Москва</code>",
#                     parse_mode="HTML"
#                 )
#                 return

#             info = get_city_info(city)
#             if not info:
#                 await message.answer(
#                     "❌ Город не найден. Проверьте правильность написания.",
#                     parse_mode="HTML"
#                 )
#                 return

#             city_id = info["id"]
#             city_url_openweather = f"https://openweathermap.org/city/{city_id}"

#             answer = (
#                 f"🏙 <b>Информация о городе:</b> {info['city']}, {info['country']}\n\n"
#                 f"👥 <b>Население:</b> {info['population']} человек\n"
#                 f"🌅 <b>Рассвет:</b> {info['sunrise']}\n"
#                 f"🌇 <b>Закат:</b> {info['sunset']}\n\n"
#                 f"🔗 <a href='{city_url_openweather}'>Проверить в OpenWeatherMap</a>"
#             )
#             await message.answer(answer, parse_mode="HTML", disable_web_page_preview=True)
#         else:
#             await message.answer(
#                 "⚠️ Укажите город. Пример: <code>/info Москва</code>",
#                 parse_mode="HTML"
#             )