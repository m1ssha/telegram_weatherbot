import re
import logging
from datetime import datetime

from aiogram import types, Bot
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram import Dispatcher
from aiogram.types import FSInputFile, BufferedInputFile

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import aiosqlite
import matplotlib.pyplot as plt
import io

from API.weather import get_dailyforecast
from messages import messages

DB_FILE = "subscriptions.db"
scheduler = AsyncIOScheduler()

LIMIT = 10

async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            """CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                city TEXT,
                notify_time TEXT,
                UNIQUE(user_id, city, notify_time) -- Предотвращает дублирование одной подписки
            )"""
        )
        await db.commit()



async def get_user_subscriptions(user_id: int):
    """Получает подписки конкретного пользователя."""
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT city, notify_time FROM subscriptions WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchall()


async def count_user_subscriptions(user_id: int):
    """Считает количество подписок пользователя."""
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT COUNT(*) FROM subscriptions WHERE user_id = ?", (user_id,)) as cursor:
            count = await cursor.fetchone()
            return count[0] if count else 0


async def add_subscription(user_id: int, city: str, notify_time: str):
    """Добавляет подписку в базу данных, если их меньше 10."""
    current_count = await count_user_subscriptions(user_id)
    
    if current_count >= LIMIT:
        return False

    try:
        async with aiosqlite.connect(DB_FILE) as db:
            await db.execute(
                "INSERT INTO subscriptions (user_id, city, notify_time) VALUES (?, ?, ?)",
                (user_id, city, notify_time),
            )
            await db.commit()
        return True

    except Exception as e:
        logging.error(f"Ошибка при добавлении подписки: {e}")
        return False



async def get_subscriptions():
    """Получает все подписки из базы данных."""
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT user_id, city, notify_time FROM subscriptions") as cursor:
            return await cursor.fetchall()


async def send_daily_forecast(bot: Bot):
    import matplotlib.dates as mdates
    """Отправляет прогноз погоды подписчикам с графиком температуры."""
    subscriptions = await get_subscriptions()
    now = datetime.now().strftime("%H:%M")

    for user_id, city, notify_time in subscriptions:
        if notify_time == now:
            forecast_data, city_id = get_dailyforecast(city)
            if forecast_data:
                city_url_openweather = f"https://openweathermap.org/city/{city_id}"
                forecast_text = messages.daily_forecast_message(city, forecast_data, city_url_openweather)

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

                try:
                    await bot.send_photo(user_id, photo=photo, parse_mode="HTML", disable_notification=True)
                    await bot.send_message(user_id, forecast_text, parse_mode="HTML", disable_web_page_preview=True)

                except Exception as e:
                    logging.error(f"Ошибка отправки сообщения пользователю {user_id}: {e}")



def register_subscribe(dp: Dispatcher):
    @dp.message(Command("subscribe"))
    async def subscribe_handler(message: Message, command):
        if message.chat.type != "private":
            await message.answer("🚫 Эта команда доступна только в личных сообщениях с ботом.")
            return
        
        if not command.args:
            await message.answer(messages.warning_subscribe_input, parse_mode="HTML")
            return

        args = command.args.split()
        if len(args) != 2:
            await message.answer(messages.error_subscribe_format, parse_mode="HTML")
            return

        city, notify_time = args
        if not re.match(r"^[a-zA-Zа-яА-ЯёЁ\s\-]{2,50}$", city):
            await message.answer(messages.error_city_subscribe, parse_mode="HTML")
            return
        
        city = city.replace("'", "").replace('"', "").replace(";", "").replace("--", "")

        try:
            normalized_time = datetime.strptime(notify_time, "%H:%M").strftime("%H:%M")
        except ValueError:
            await message.answer(messages.error_subscribe_time, parse_mode="HTML")
            return

        success = await add_subscription(message.from_user.id, city, normalized_time)
        if not success:
            await message.answer(f"{messages.error_subscribe_not_success} ({LIMIT})")
            return

        await message.answer(messages.success_subscribe.format(city=city, time=normalized_time), parse_mode="HTML")


def schedule_daily_forecasts(bot: Bot):
    """Запускает задачу, которая проверяет подписки каждую минуту."""
    scheduler.add_job(send_daily_forecast, "cron", minute="*", args=[bot])
    scheduler.start()
