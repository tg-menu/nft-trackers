 import asyncio
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from aiogram import Bot
from telethon import TelegramClient

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8789847797:AAGmwEa5om3cO4AA1CBraAfCMQl2KyDXqCs"
CHAT_ID = -1004415141036
THREAD_ID = 2

# Твои реальные данные API
API_ID = 32664392
API_HASH = "ebdb1e9063562eb00e75ef20336869e6"

bot = Bot(token=BOT_TOKEN)
seen_gifts = set()

# Веб-сервер для Render (чтобы бот не засыпал)
class SimpleHandler(BaseHTTPRequestHandler):
    do_GET = lambda self: (self.send_response(200), self.end_headers(), self.wfile.write(b"NFT Tracker is active!"))

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# Функция отправки карточки подарка
async def send_gift_alert(gift_id, username, has_premium, price, photo_url):
    if gift_id in seen_gifts:
        return
    seen_gifts.add(gift_id)
    
    premium_status = "💎 Есть" if has_premium else "Нет"
    
    caption = (
        f"🎁 **Новый подарок на продажу!**\n\n"
        f"👤 **Продавец:** @{username}\n"
        f"⭐ **Telegram Premium:** {premium_status}\n"
        f"💰 **Цена:** {price}"
    )
    
    try:
        await bot.send_photo(
            chat_id=CHAT_ID,
            message_thread_id=THREAD_ID,
            photo=photo_url,
            caption=caption,
            parse_mode="Markdown"
        )
        print(f"Отправлен новый подарок от @{username}")
    except Exception as e:
        print(f"Ошибка отправки: {e}")

# Функция мониторинга маркетплейса через UserBot
async def monitor_marketplace():
    client = TelegramClient('session_name', API_ID, API_HASH)
    
    try:
        await client.start()
        print("UserBot успешно авторизован!")
    except Exception as e:
        print(f"Ошибка авторизации UserBot: {e}")
        return

    while True:
        try:
            # Логика получения данных с маркетплейса
            pass
        except Exception as e:
            print(f"Ошибка в мониторинге: {e}")
            
        await asyncio.sleep(15)

async def main():
    print("Fast NFT Tracker запускается...")
    
    # Отправляем стартовое сообщение в топик для проверки
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            message_thread_id=THREAD_ID,
            text="🚀 **Бот и UserBot успешно запущены на сервере!**",
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Ошибка отправки старта: {e}")

    # Запуск фонового мониторинга
    asyncio.create_task(monitor_marketplace())

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    asyncio.run(main())
