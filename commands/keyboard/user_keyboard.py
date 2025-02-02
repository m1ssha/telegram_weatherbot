from aiogram.types import ReplyKeyboardMarkup
from commands.keyboard.buttons_keyboard import btn_help, btn_weather, btn_forecast, btn_mysubscriptions, btn_unsubscribe

user_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [btn_weather, btn_forecast],
        [btn_mysubscriptions, btn_unsubscribe],
        [btn_help]
    ],
    resize_keyboard=True
)