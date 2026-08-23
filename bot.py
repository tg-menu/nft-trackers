import asyncio
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from aiogram import Bot
from telethon import TelegramClient
from telethon.sessions import StringSession
import aiohttp

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8789847797:AAGmwEa5om3cO4AA1CBraAfCMQl2KyDXqCs"
CHAT_ID = -1004415141036
THREAD_ID = 2

API_ID = 32664392
API_HASH = "ebdb1e9063562eb00e75ef20336869e6"

# Твоя рабочая сессия UserBot
SESSION_STRING = "1ApWapzMBu5fv8cjP5T5aBIOqMyX8QKIj6vqqaMTAJkiho3yTPD9sK1q-Qb3Lva_cTzbOwCVgsIMzVvTVy5Cb85AIGteJfUWPdheMJFbhICOzarUplCRkrNcbXniR1XG2vqwDiI9c6fxJa3C3P2WPMiKG1Hp-pEPJ0Dp-TWpE_G9IjkUfXR3Y9c7Umnb4XHLuP2X0ElUDNOjEbHJnolEH0qNP-Y2jZWk3_kBbAZZ1MNTzNx_zApsIu99pUmlNwL_mgBfe6ytEgCChHFzGYUfba82q-4O0vatduebuJ5uL0bJOsbL1g3Dz1J73GB4idIcVaXx7zrtNFi1LhmH3JS3Zdq-7dcu-u4U="

bot = Bot(token=BOT_TOKEN)
seen_gifts = set()

# Веб-сервер для Render, чтобы бот не засыпал
class SimpleHandler(BaseHTTPRequestHandler):
    do_GET = lambda self: (self.send_response(200), self.end_headers(), self.wfile.write(b"NFT Tracker is active!"))

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# Функция отправки карточки подарка в твой топик
async def send_gift_alert(gift_id, username, has_premium, price, photo_url):
    if gift_id in seen_gifts:
        return
    seen_gifts.add(gift_id)
    
    premium_status = "💎 Есть" if has_premium else "❌ Нет"
    
    caption = (
        f"🎁 **Новый коллекционный подарок!**\n\n"
        f"👤 **Продавец:** @{username} ([Написать](https://t.me/{username}))\n"
        f"⭐ **Telegram Premium:** {premium_status}\n"
        f"💰 **Цена:** {price} Stars"
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
        print(f"Ошибка отправки сообщения: {e}")

# Функция мониторинга маркетплейса подарков
async def monitor_marketplace():
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    
    try:
        await client.start()
        print("UserBot успешно подключен к аккаунту и запущен на сервере!")
    except Exception as e:
        print(f"Ошибка подключения UserBot: {e}")
        return

    while True:
        try:
            # Здесь бот опрашивает источник / маркетплейс подарков.
            # Как только появляется новый выставленный лог/подарок, 
            # скрипт считывает параметры (gift_id, username, has_premium, price, photo_url)
            # и передает их в функцию отправки:
            # 
            # Пример вызова:
            # await send_gift_alert("gift_12345", "durov", True, "500", "https://example.com/gift.png")
            
            pass
        except Exception as e:
            print(f"Ошибка в цикле мониторинга: {e}")
            
        await asyncio.sleep(15)

async def main():
    print("Fast NFT Tracker запущен...")
    
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            message_thread_id=THREAD_ID,
            text="🚀 **Трекер подарков успешно запущен и работает!**",
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Ошибка отправки старта в чат: {e}")

    # Запускаем фоновый мониторинг
    asyncio.create_task(monitor_marketplace())

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    asyncio.run(main())
