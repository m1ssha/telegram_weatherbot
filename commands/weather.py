import re
import logging
from aiogram import types
from aiogram.filters import Command
from aiogram.types import Message
from weather_api import get_weather

def escape_html(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def register_weather(dp):
    @dp.message(Command("weather"))
    async def weather_handler(message: Message, command):
        if command.args:
            city = command.args.strip()

            if not re.match(r"^[a-zA-Zа-яА-ЯёЁ\s\-]+$", city):
                logging.warning(f"Ошибка ввода города: {message.text}")
                await message.answer(
                    "🚫 Ошибка: название города должно содержать только буквы и пробелы. Пример: <code>/weather Москва</code>",
                    parse_mode="HTML"
                )
                return

            weather = get_weather(city)

            if not weather or "city_id" not in weather:
                logging.error(f"Город не найден: {city}")
                await message.answer(
                    "❌ Город не найден. Проверьте правильность написания и попробуйте снова.",
                    parse_mode="HTML"
                )
                return

            city_url_openweather = f"https://openweathermap.org/city/{weather['city_id']}"

            answer = (
                f"🏙 <b>Город:</b> {escape_html(weather['city'])}\n"
                f"🌡 <b>Температура:</b> {weather['temp']}°C\n"
                f"🥶 <b>Ощущается как:</b> {weather['feels_like']}°C\n"
                f"💨 <b>Ветер:</b> {escape_html(weather['windspeed'])}\n"
                f"🌫 <b>Давление:</b> {weather['pressure']} мм рт. ст.\n"
                f"💧 <b>Влажность:</b> {weather['humidity']}%\n"
                f"🌦 <b>Погода:</b> {escape_html(weather['description'].capitalize())}\n\n"
                f"🔗 <a href='{city_url_openweather}'>Проверить в OpenWeatherMap</a>"
            )

            logging.info(f"Отправлен прогноз погоды для {city}")
            await message.answer(answer, parse_mode="HTML", disable_web_page_preview=True)

        else:
            logging.warning(
                f"Команда /weather была вызвана без указания города пользователем {message.from_user.full_name}"
            )
            await message.answer(
                "⚠️ Пожалуйста, укажите город. Пример: <code>/weather Москва</code>",
                parse_mode="HTML"
            )
