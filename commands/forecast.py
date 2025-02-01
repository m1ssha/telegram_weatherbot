import re
from aiogram import types
from aiogram.filters import Command
from aiogram.types import Message
from weather_api import get_weather_forecast

def register_forecast(dp):
    @dp.message(Command("forecast"))
    async def forecast_handler(message: Message, command):
        if command.args:
            args = command.args.split()
            city = args[0]

            if not re.match(r"^[a-zA-Zа-яА-ЯёЁ\s\-]+$", city):
                await message.answer(
                    "🚫 Ошибка: название города должно содержать только буквы. Пример: <code>/forecast Москва 12</code>",
                    parse_mode="HTML"
                )
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
                    await message.answer(
                        "⚠️ Ошибка: Время прогноза должно быть числом (часы или дни). Пример: <code>/forecast Москва 12</code>",
                        parse_mode="HTML"
                    )
                    return

            forecast_data, city_id = get_weather_forecast(city, hours=hours, days=days)

            if not forecast_data:
                await message.answer(
                    "❌ Город не найден. Проверьте правильность написания.",
                    parse_mode="HTML"
                )
                return
            
            city_url_openweather = f"https://openweathermap.org/city/{city_id}"
            forecast_text = (
                f"📅 Прогноз погоды в городе {city} на {hours} часов:\n"
                f"🔗 <a href='{city_url_openweather}'>Проверить в OpenWeatherMap</a>\n\n"
            )
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
            await message.answer(
                "⚠️ Укажите город. Пример: <code>/forecast Москва 12</code>",
                parse_mode="HTML"
            )
