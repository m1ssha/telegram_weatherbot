import re
import logging
from aiogram import types
from aiogram.filters.command import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import io
from aiogram.types import BufferedInputFile
from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from API.weather import get_weather_forecast
from messages import messages

class ForecastState(StatesGroup):
    waiting_for_city = State()

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

            hours = 12
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
            await message.answer(messages.warning_forecast_input, reply_markup=get_city_keyboard(), parse_mode="HTML")

    @dp.callback_query(lambda c: c.data.startswith("forecast_"))
    async def city_callback_handler(callback: CallbackQuery, state: FSMContext):
        from buttons.citymap import city_map_forecast as city_map

        city_key = callback.data
        if city_key in city_map:
            city = city_map[city_key]

            await callback.message.delete()

            await send_forecast_info(callback.message, city, 12, 0, show_back_button=True)
            await callback.answer()

        elif city_key == "forecast_custom":
            await callback.message.delete()

            await callback.message.answer("Введите название города:")
            
            await state.set_state(ForecastState.waiting_for_city)
            await callback.answer()

    @dp.message(ForecastState.waiting_for_city)
    async def process_city_input(message: Message, state: FSMContext):
        """Обработчик ввода города после выбора 'Выбрать другой город'."""

        city = message.text.strip()

        if not re.match(r"^[a-zA-Zа-яА-ЯёЁ\s\-]+$", city):
            await message.answer("Некорректное название города. Попробуйте снова:")
            return
        
        await state.clear()
        await send_forecast_info(message, city, 6, 0, show_back_button=True)

    @dp.callback_query(lambda c: c.data == "back_to_forecast_cities")
    async def back_to_forecast_cities_handler(callback: CallbackQuery):
        """Обработчик кнопки "Вернуться к выбору городов".""" 
        try:
            await callback.message.delete()
            await callback.message.answer(
                messages.warning_choose_city,
                reply_markup=get_city_keyboard(),
                parse_mode="HTML"
            )
        except Exception as e:
            logging.error(f"Ошибка при возврате к выбору городов: {e}")
            await callback.message.answer(
                messages.warning_choose_city,
                reply_markup=get_city_keyboard(),
                parse_mode="HTML"
            )

        await callback.answer()

async def send_forecast_info(message: Message, city: str, hours: int, days: int, show_back_button=False):
    from datetime import datetime
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import io
    import logging
    from aiogram.types import BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton

    forecast_data, city_id = get_weather_forecast(city, hours=hours, days=days)

    if not forecast_data:
        logging.error(f"Город не найден: {city}")
        await message.reply(messages.error_find_city, parse_mode="HTML")
        return

    times = [datetime.strptime(entry["дата и время"], "%d.%m.%Y %H:%M") for entry in forecast_data]
    temperatures = [entry["температура"] for entry in forecast_data]

    start_time = times[0].strftime("%H:%M") if times else "?"
    end_time = times[-1].strftime("%H:%M") if times else "?"
    date = times[0].strftime("%d.%m.%Y") if times else "?"

    bg_color = "#242424"
    line_color = "#00c8ff"
    text_color = "white"
    grid_color = "gray"

    plt.figure(figsize=(12, 6), facecolor=bg_color)
    ax = plt.gca()
    ax.set_facecolor(bg_color)

    plt.plot(times, temperatures, linestyle="-", color=line_color, marker="o", markersize=5, label="Температура (°C)")

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.xticks(rotation=45, fontsize=10, color=text_color)
    plt.yticks(fontsize=10, color=text_color)

    plt.xlabel("Время", fontsize=12, fontweight="bold", color=text_color)
    plt.ylabel("Температура (°C)", fontsize=12, fontweight="bold", color=text_color)
    plt.title(f"Температура в городе {city} с {start_time} по {end_time} на {date}", fontsize=14, fontweight="bold", color=text_color)

    plt.grid(True, linestyle="--", alpha=0.5, color=grid_color)
    ax.yaxis.grid(True, linestyle="--", alpha=0.5, color=grid_color)

    plt.legend(fontsize=10, facecolor="#222222", edgecolor="white", labelcolor="white")

    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format="png", bbox_inches="tight", dpi=200, facecolor=bg_color, pad_inches=0.5)
    img_bytes.seek(0)
    plt.close()

    photo = BufferedInputFile(img_bytes.getvalue(), filename="weather_chart.png")

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
        if len(forecast_text) < 1024:
            await message.answer_photo(photo, caption=forecast_text, parse_mode="HTML", reply_markup=keyboard)
        else:
            await message.answer_photo(photo)
            await message.answer(forecast_text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)
    except Exception as e:
        logging.error(f"Ошибка при отправке /forecast: {e}")
