import logging
import re
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from dotenv import load_dotenv
from weather_api import get_weather

load_dotenv()
TOKEN = os.getenv("TELEGRAM_API_KEY")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8")
    ]
)

client = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: Message):
    logging.info(f"Пользователь {message.from_user.full_name} ({message.from_user.id}) вызвал команду /start")
    answer = f"Привет, {message.from_user.full_name}! Я бот, который подскажет тебе погоду.\n\n"f"Вся информация по использованию в /help."
    await message.answer(answer, parse_mode="HTML")

@dp.message(Command("help"))
async def help_handler(message: Message):
    logging.info(f"Пользователь {message.from_user.full_name} ({message.from_user.id}) вызвал команду /help")

    answer = (
        "📌 <b>Меню помощи</b> 📌\n\n"
        "<b>/weather [город]</b> - Получает текущую погоду в указанном городе.\n"
        "  🔹 <i>Пример:</i> <code>/weather Москва</code>\n\n"
        "<b>/forecast [город] [часы/дни]</b> - Прогноз погоды на указанное время.\n"
        "По умолчанию выводится прогноз погоды на ближайшие 6 часов\n"
        "  🔹 <i>Пример:</i> <code>/forecast Москва 12</code> (на 12 часов)\n"
        "  🔹 <i>Пример:</i> <code>/forecast Москва 48</code> (на 2 дня)\n\n"
        "<b>/info [город]</b> - Выводит информацию о городе\n\n"
        "💡 Бот использует данные OpenWeatherMap 🌍"
    )

    await message.answer(answer, parse_mode="HTML")


def escape_html(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

@dp.message(Command("weather"))
async def weather_handler(message: Message, command: CommandObject):
    if command.args:
        city = command.args.strip()

        if not re.match(r"^[a-zA-Zа-яА-ЯёЁ\s\-]+$", city):
            logging.warning(f"Ошибка ввода города: {message.text}")
            await message.answer("🚫 Ошибка: название города должно содержать только буквы и пробелы. Пример: <code>/weather Москва</code>", parse_mode="HTML")
            return

        weather = get_weather(city)

        if not weather or "city_id" not in weather:
            logging.error(f"Город не найден: {city}")
            await message.answer("❌ Город не найден. Проверьте правильность написания и попробуйте снова.", parse_mode="HTML")
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
        logging.warning(f"Команда /weather была вызвана без указания города пользователем {message.from_user.full_name}")
        await message.answer("⚠️ Пожалуйста, укажите город. Пример: <code>/weather Москва</code>", parse_mode="HTML")

@dp.message(Command("forecast"))
async def forecast_handler(message: Message, command: CommandObject):
    from weather_api import get_weather_forecast
    if command.args:
        args = command.args.split()
        city = args[0]

        if not re.match(r"^[a-zA-Zа-яА-ЯёЁ\s\-]+$", city):
            await message.answer("🚫 Ошибка: название города должно содержать только буквы. Пример: <code>/forecast Москва 12</code>", parse_mode="HTML")
            return

        hours = 6
        days = 0

        if len(args) > 1:
            try:
                value = int(args[1])
                if value > 24:
                    days = value // 24
                else:
                    hours = value
            except ValueError:
                await message.answer("⚠️ Ошибка: Время прогноза должно быть числом (часы или дни). Пример: <code>/forecast Москва 12</code>", parse_mode="HTML")
                return

        forecast_data, city_id = get_weather_forecast(city, hours=hours, days=days)

        if not forecast_data:
            await message.answer("❌ Город не найден. Проверьте правильность написания.", parse_mode="HTML")
            return
        
        city_url_openweather = f"https://openweathermap.org/city/{city_id}"
        forecast_text = f"📅 Прогноз погоды в городе {city} на {hours} часов:\n🔗 <a href='{city_url_openweather}'>Проверить в OpenWeatherMap</a>\n\n"
        for entry in forecast_data:
            forecast_text += (
                f"<b>{entry['дата и время']}</b>\n"
                f"🌡 Температура: {entry['температура']}°C\n"
                f"🥶 Ощущается как: {entry['ощущается как']}°C\n"
                f"💧 Влажность: {entry['влажность']}%\n"
                f"🌫 Давление: {entry['давление']} мм рт. ст.\n"
                f"💨 Ветер: {entry['ветер']}\n"
                f"🌦 Погода: {entry['погода'].capitalize()}\n\n"
            )

        await message.answer(forecast_text, parse_mode="HTML", disable_web_page_preview=True)

    else:
        await message.answer("⚠️ Укажите город. Пример: <code>/forecast Москва 12</code>", parse_mode="HTML")

@dp.message(Command("info"))
async def city_info_handler(message: Message, command: CommandObject):
    from weather_api import get_city_info
    if command.args:
        city = command.args.strip()

        if not re.match(r"^[a-zA-Zа-яА-ЯёЁ\s\-]+$", city):
            logging.warning(f"Ошибка ввода города: {message.text}")
            await message.answer("🚫 Ошибка: название города должно содержать только буквы и пробелы. Пример: <code>/weather Москва</code>", parse_mode="HTML")
            return

        info = get_city_info(city)
        if not info:
            await message.answer("❌ Город не найден. Проверьте правильность написания.", parse_mode="HTML")
            return
        city_id = info["id"]
        city_url_openweather = f"https://openweathermap.org/city/{city_id}"


        answer = (
            f"🏙 <b>Информация о городе:</b> {info['city']}, {info['country']}\n\n"
            f"👥 <b>Население:</b> {info['population']} человек\n"
            f"🌅 <b>Рассвет:</b> {info['sunrise']}\n"
            f"🌇 <b>Закат:</b> {info['sunset']}\n\n"
            f"🔗 <a href='{city_url_openweather}'>Проверить в OpenWeatherMap</a>"
        )

        
        await message.answer(answer, parse_mode="HTML", disable_web_page_preview=True)