import aiosqlite


DB_PATH = "bot_data.db"


async def init_db():
    """Создает таблицы, если их нет"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                chat_id INTEGER PRIMARY KEY,
                chat_title TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT
            )
        """)
        await db.commit()


async def add_user(user_id: int, username: str, full_name: str):
    """Добавляет пользователя в базу данных"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO users (user_id, username, full_name) 
            VALUES (?, ?, ?)
        """, (user_id, username, full_name))
        await db.commit()

async def get_all_users():
    """Получает список всех пользователей из базы данных"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT user_id, username, full_name FROM users")
        users = await cursor.fetchall()
        return users


async def add_chat(chat_id: int, chat_title: str):
    """Добавляет чат в базу данных"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO chats (chat_id, chat_title) 
            VALUES (?, ?)
        """, (chat_id, chat_title))
        await db.commit()


async def remove_chat(chat_id: int):
    """Удаляет чат из базы данных"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM chats WHERE chat_id = ?", (chat_id,))
        await db.commit()


async def get_all_chats():
    """Получает список всех чатов из базы данных"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT chat_id, chat_title FROM chats")
        chats = await cursor.fetchall()
        return chats
