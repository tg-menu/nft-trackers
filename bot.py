import asyncio
import os
import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8789847797:AAGmwEa5om3cO4AA1CBraAfCMQl2KyDXqCs"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Временное хранилище выбора пользователя
user_selected_models = {}

# Список доступных подарков для меню
GIFT_MODELS = [
    "FaithAmulet", "FreshSocks", "GingerCookie", 
    "HappyBrownie", "HolidayDrink", "HomemadeCake", 
    "IceCream", "InstantRamen", "JesterHat", "LolPop"
]

# --- РАБОТА С БАЗОЙ ДАННЫХ ---
def init_db():
    conn = sqlite3.connect("gifts.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_gifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            model TEXT,
            price INTEGER
        )
    """)
    
    # Добавим немного стартовых тестовых данных для примера, чтобы поиск сразу выдавал результаты
    cursor.execute("SELECT COUNT(*) FROM user_gifts")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ("WMBT13579", "LolPop", 450),
            ("neherexwer", "LolPop", 460),
            ("k2rtcoba1", "LolPop", 470),
            ("heartalarmsignal", "LolPop", 480),
            ("indeseada", "LolPop", 490),
            ("MJDIGUO", "LolPop", 500),
            ("astya_lover", "LolPop", 510),
            ("Annushka_1301", "LolPop", 520),
            ("p0lya777", "LolPop", 530),
            ("LGddae", "LolPop", 540),
            ("lonelyrous", "LolPop", 550),
            ("dpsdx", "LolPop", 560),
            ("andryshook", "LolPop", 570),
            ("zs418888", "LolPop", 580),
            ("ofbeo", "LolPop", 590),
            ("FreshSocks_user1", "FreshSocks", 300),
            ("IceCream_owner", "IceCream", 400)
        ]
        cursor.executemany("INSERT INTO user_gifts (username, model, price) VALUES (?, ?, ?)", sample_data)
        conn.commit()
    conn.close()

init_db()

def search_gifts_in_db(models, page=1, per_page=5):
    conn = sqlite3.connect("gifts.db")
    cursor = conn.cursor()
    
    if not models:
        conn.close()
        return [], 0
    
    placeholders = ','.join(['?'] * len(models))
    
    # Считаем общее количество
    cursor.execute(f"SELECT COUNT(*) FROM user_gifts WHERE model IN ({placeholders})", models)
    total_count = cursor.fetchone()[0]
    
    # Достаем элементы для текущей страницы
    offset = (page - 1) * per_page
    cursor.execute(f"""
        SELECT username, model, price FROM user_gifts 
        WHERE model IN ({placeholders}) 
        LIMIT ? OFFSET ?
    """, models + [per_page, offset])
    
    results = cursor.fetchall()
    conn.close()
    return results, total_count

# --- HTTP-сервер для Render ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Database Search Bot is active!")
    def log_message(self, format, *args):
        pass

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# --- КЛАВИАТУРЫ ---
def get_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Поиск NFT / Подарков", callback_data="menu_search")],
        [InlineKeyboardButton(text="👤 Мой профиль", callback_data="profile")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")],
        [InlineKeyboardButton(text="🛟 Поддержка", callback_data="support")]
    ])

def get_search_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Поиск по модели - точный поиск", callback_data="select_models")],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
    ])

def get_models_keyboard(selected=None):
    if selected is None:
        selected = []
    
    keyboard = []
    for model in GIFT_MODELS:
        mark = "✓ " if model in selected else ""
        keyboard.append([InlineKeyboardButton(text=f"{mark}{model} (E)", callback_data=f"toggle_{model}")])
    
    keyboard.append([InlineKeyboardButton(text="➡️ Начать поиск", callback_data="start_search_1")])
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="menu_search")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# --- ХЕНДЛЕРЫ ---
@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    user_selected_models[user_id] = []
    
    text = f"✨ **Привет, @{message.from_user.username or 'друг'}!**\n\nЭто бот для поиска подарков и владельцев через базу данных."
    await message.answer(text, reply_markup=get_main_menu(), parse_mode="Markdown")

@dp.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery):
    await callback.message.edit_text("✨ **Главное меню:**", reply_markup=get_main_menu(), parse_mode="Markdown")

@dp.callback_query(F.data == "menu_search")
async def cb_menu_search(callback: CallbackQuery):
    text = (
        "🔍 **Выберите тип поиска:**\n\n"
        "• Рандом поиск - поиск по режимам\n"
        "• Поиск по модели - точный поиск по конкретным NFT подаркам"
    )
    await callback.message.edit_text(text, reply_markup=get_search_menu(), parse_mode="Markdown")

@dp.callback_query(F.data == "select_models")
async def cb_select_models(callback: CallbackQuery):
    user_id = callback.from_user.id
    selected = user_selected_models.get(user_id, [])
    
    text = "📦 **Выберите модели подарков для поиска:**"
    await callback.message.edit_text(text, reply_markup=get_models_keyboard(selected), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("toggle_"))
async def cb_toggle_model(callback: CallbackQuery):
    user_id = callback.from_user.id
    model = callback.data.split("_")[1]
    
    if user_id not in user_selected_models:
        user_selected_models[user_id] = []
        
    if model in user_selected_models[user_id]:
        user_selected_models[user_id].remove(model)
    else:
        user_selected_models[user_id].append(model)
        
    selected = user_selected_models[user_id]
    await callback.message.edit_reply_markup(reply_markup=get_models_keyboard(selected))
    await callback.answer(f"Выбор изменен: {model}")

@dp.callback_query(F.data.startswith("start_search_"))
async def cb_start_search(callback: CallbackQuery):
    user_id = callback.from_user.id
    selected = user_selected_models.get(user_id, [])
    
    if not selected:
        # Если ничего не выбрали, по умолчанию ищем LolPop для примера
        selected = ["LolPop"]
        
    page = int(callback.data.split("_")[2])
    per_page = 5
    
    results, total_count = search_gifts_in_db(selected, page=page, per_page=per_page)
    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
    
    models_str = ", ".join(selected)
    
    results_text = (
        f"🔍 **Результаты поиска по модели:**\n"
        f"🏷 Модели: `{models_str}`\n"
        f"Шаблон: Стандартный\n"
        f"Найдено пользователей: {total_count}\n\n"
    )
    
    if results:
        for idx, (username, model, price) in enumerate(results, start=1):
            real_idx = (page - 1) * per_page + idx
            results_text += f"{real_idx}. @{username} | [Написать](https://t.me/{username}) (🎁 {model}, 💰 {price}★)\n"
    else:
        results_text += "❌ Ничего не найдено по вашему запросу."
        
    results_text += f"\n**Страница {page} / {total_pages}**"
    
монетки_кнопок = []
    if page > 1:
        монетки_кнопок.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"start_search_{page - 1}"))
    if page < total_pages:
        монетки_кнопок.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"start_search_{page + 1}"))
        
    nav_row = монетки_кнопок if монетки_кнопок else []
    
    pagination_kb = InlineKeyboardMarkup(inline_keyboard=[
        nav_row,
        [InlineKeyboardButton(text="🔄 Искать снова", callback_data="select_models")],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")]
    ])
    
    try:
        await callback.message.edit_text(results_text, reply_markup=pagination_kb, parse_mode="Markdown", disable_web_page_preview=True)
    except Exception:
        pass

@dp.callback_query(F.data == "profile")
async def cb_profile(callback: CallbackQuery):
    await callback.message.edit_text("👤 **Ваш профиль:**\n\nБаланс: 40 Звёзд\nСтатус: Активен", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]]), parse_mode="Markdown")

@dp.callback_query(F.data == "settings")
async def cb_settings(callback: CallbackQuery):
    await callback.message.edit_text("⚙️ **Настройки:**\n\nЗдесь можно настроить параметры поиска.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]]), parse_mode="Markdown")

@dp.callback_query(F.data == "support")
async def cb_support(callback: CallbackQuery):
    await callback.message.edit_text("🛟 **Поддержка:**\n\nПо всем вопросам пишите администратору.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]]), parse_mode="Markdown")

async def main():
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    print("Интерактивный поисковый бот с БД запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
