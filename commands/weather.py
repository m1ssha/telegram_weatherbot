import re
import logging
from aiogram import types
from aiogram.filters import CommandObject
from aiogram.filters.command import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.enums import ChatType
from aiogram import Dispatcher

from weather_api import get_weather
from messages import messages

def escape_html(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def get_city_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Москва", callback_data="weather_Moscow")],
            [InlineKeyboardButton(text="Санкт-Петербург", callback_data="weather_SPB")],
            [InlineKeyboardButton(text="Калининград", callback_data="weather_Kaliningrad")],
            [InlineKeyboardButton(text="Калуга", callback_data="weather_Kaluga")],
            [InlineKeyboardButton(text="Иваново", callback_data="weather_Ivanovo")],
            [InlineKeyboardButton(text="Пермь", callback_data="weather_Perm")],
            [InlineKeyboardButton(text="Ташкент", callback_data="weather_Tashkent")],
            [InlineKeyboardButton(text="Выбрать другой город", callback_data="weather_custom")],
        ]
    )

def register_weather(dp: Dispatcher):
    @dp.message(Command("weather"))
    async def weather_handler(message: Message, command: CommandObject):
        city = command.args

        if city:
            city = city.strip()
            if not re.match(r"^[a-zA-Zа-яА-ЯёЁ\s\-]+$", city):
                logging.warning(f"Ошибка ввода города: {message.text}")
                await message.reply(messages.error_city,parse_mode="HTML")
                return

            await send_weather_info(message, city)

        else:
            logging.warning(f"Команда /weather вызвана без указания города пользователем {message.from_user.full_name}")

            await message.answer(messages.warning_city, reply_markup=get_city_keyboard())

    @dp.callback_query(lambda c: c.data.startswith("weather_"))
    async def city_callback_handler(callback: CallbackQuery):
        """Обработчик кнопок выбора города."""
        city_map = {
            "weather_Moscow": "Москва",
            "weather_SPB": "Санкт-Петербург",
            "weather_Tashkent": "Ташкент",
            "weather_Kaliningrad": "Калининград",
            "weather_Kaluga": "Калуга",
            "weather_Ivanovo": "Иваново",
            "weather_Perm": "Пермь",
        }
        city_key = callback.data
        if city_key in city_map:
            city = city_map[city_key]
            await send_weather_info(callback.message, city, show_back_button=True)
            await callback.answer()
        elif city_key == "weather_custom":
            await callback.message.edit_text(messages.info_city_weather, parse_mode="HTML")
            await callback.answer()

    @dp.callback_query(lambda c: c.data == "back_to_cities")
    async def back_to_cities_handler(callback: CallbackQuery):
        """Обработчик кнопки "Вернуться к выбору городов"."""
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

async def send_weather_info(message: Message, city: str, show_back_button=False):
    weather = get_weather(city)

    if not weather or "city_id" not in weather:
        logging.error(f"Город не найден: {city}")
        await message.reply(messages.error_find_city, parse_mode="HTML")
        return

    city_url_openweather = f"https://openweathermap.org/city/{weather['city_id']}"

    answer = messages.weather_message(weather, city_url_openweather)

    keyboard = None
    if show_back_button:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text = messages.back_to_city_choice, callback_data="back_to_cities")]
            ]
        )

    try:
        await message.edit_text(answer, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)
    except:
        await message.answer(answer, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)
