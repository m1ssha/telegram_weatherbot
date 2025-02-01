import re
import logging
from aiogram import types
from aiogram.filters.command import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram import Dispatcher

from weather_api import get_weather_forecast
from messages import messages

def get_city_keyboard():
    """Создаёт клавиатуру с городами для прогноза погоды."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Москва", callback_data="forecast_Moscow")],
            [InlineKeyboardButton(text="Санкт-Петербург", callback_data="forecast_SPB")],
            [InlineKeyboardButton(text="Калининград", callback_data="forecast_Kaliningrad")],
            [InlineKeyboardButton(text="Калуга", callback_data="forecast_Kaluga")],
            [InlineKeyboardButton(text="Иваново", callback_data="forecast_Ivanovo")],
            [InlineKeyboardButton(text="Пермь", callback_data="forecast_Perm")],
            [InlineKeyboardButton(text="Ташкент", callback_data="forecast_Tashkent")],
            [InlineKeyboardButton(text="Выбрать другой город", callback_data="forecast_custom")],
        ]
    )

def register_forecast(dp: Dispatcher):
    @dp.message(Command("forecast"))
    async def forecast_handler(message: Message, command):
        """Обработчик команды /forecast."""
        if command.args:
            args = command.args.split()
            city = args[0]

            if not re.match(r"^[a-zA-Zа-яА-ЯёЁ\s\-]+$", city):
                await message.answer(messages.error_city_forecast, parse_mode="HTML")
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
                    await message.answer(messages.error_forecast_time, parse_mode="HTML")
                    return

            await send_forecast_info(message, city, hours, days)

        else:
            await message.answer(messages.warning_forecast_input, reply_markup=get_city_keyboard(), parse_mode = "HTML")

    @dp.callback_query(lambda c: c.data.startswith("forecast_"))
    async def city_callback_handler(callback: CallbackQuery):
        """Обработчик кнопок выбора города для прогноза."""
        city_map = {
            "forecast_Moscow": "Москва",
            "forecast_SPB": "Санкт-Петербург",
            "forecast_Tashkent": "Ташкент",
            "forecast_Kaliningrad": "Калининград",
            "forecast_Kaluga": "Калуга",
            "forecast_Ivanovo": "Иваново",
            "forecast_Perm": "Пермь",
        }
        city_key = callback.data
        if city_key in city_map:
            city = city_map[city_key]
            await send_forecast_info(callback.message, city, 6, 0, show_back_button=True)
            await callback.answer()
        elif city_key == "forecast_custom":
            await callback.message.edit_text(messages.info_city_forecast, parse_mode="HTML")
            await callback.answer()

    @dp.callback_query(lambda c: c.data == "back_to_forecast_cities")
    async def back_to_forecast_cities_handler(callback: CallbackQuery):
        """Обработчик кнопки "Вернуться к выбору городов" для прогноза."""
        try:
            await callback.message.edit_text(
                messages.warning_choose_city,
                reply_markup=get_city_keyboard()
            )
        except Exception:
            await callback.message.answer(
                messages.warning_choose_city,
                reply_markup=get_city_keyboard()
            )
        await callback.answer()

async def send_forecast_info(message: Message, city: str, hours: int, days: int, show_back_button=False):
    """Функция для отправки прогноза погоды."""
    forecast_data, city_id = get_weather_forecast(city, hours=hours, days=days)

    if not forecast_data:
        logging.error(f"Город не найден: {city}")
        await message.reply(messages.error_find_city, parse_mode="HTML")
        return

    city_url_openweather = f"https://openweathermap.org/city/{city_id}"
    forecast_text = messages.forecast_message(city, hours, forecast_data, city_url_openweather)

    keyboard = None
    if show_back_button:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=messages.back_to_city_choice, callback_data="back_to_forecast_cities")]
            ]
        )

    try:
        await message.edit_text(forecast_text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)
    except:
        await message.answer(forecast_text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)
