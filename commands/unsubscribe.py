import aiosqlite
from aiogram import Dispatcher
from aiogram.filters.command import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

DB_FILE = "subscriptions.db"

async def get_user_subscriptions(user_id: int):
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT city, notify_time FROM subscriptions WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchall()


async def remove_subscription(user_id: int, city: str, notify_time: str):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "DELETE FROM subscriptions WHERE user_id = ? AND city = ? AND notify_time = ?",
            (user_id, city, notify_time),
        )
        await db.commit()


async def remove_all_subscriptions(user_id: int):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("DELETE FROM subscriptions WHERE user_id = ?", (user_id,))
        await db.commit()


def get_unsubscribe_keyboard(subscriptions):
    keyboard = []
    
    for city, notify_time in subscriptions:
        button_text = f"📍 {city} — ⏰ {notify_time}"
        callback_data = f"unsubscribe_{city}_{notify_time}"
        keyboard.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])

    keyboard.append([InlineKeyboardButton(text="❌ Отписаться от всего", callback_data="unsubscribe_all")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def register_unsubscribe(dp: Dispatcher):
    @dp.message(Command("unsubscribe"))
    async def unsubscribe_handler(message: Message):
        if message.chat.type != "private":
            await message.answer("🚫 Эта команда доступна только в личных сообщениях с ботом.")
            return
        
        subscriptions = await get_user_subscriptions(message.from_user.id)
        
        if not subscriptions:
            await message.answer("❌ У вас нет активных подписок.")
            return

        await message.answer("Выберите подписку, от которой хотите отписаться:", 
                             reply_markup=get_unsubscribe_keyboard(subscriptions))

    @dp.callback_query(lambda c: c.data.startswith("unsubscribe_"))
    async def unsubscribe_callback_handler(callback: CallbackQuery):
        data = callback.data.split("_")
        
        if data[1] == "all":
            await remove_all_subscriptions(callback.from_user.id)
            await callback.message.edit_text("✅ Вы успешно отписались от всех подписок!")
        else:
            city = data[1]
            notify_time = data[2]
            await remove_subscription(callback.from_user.id, city, notify_time)
            await callback.message.edit_text(f"✅ Вы успешно отписались от подписки: {city} в {notify_time}")

        await callback.answer()
