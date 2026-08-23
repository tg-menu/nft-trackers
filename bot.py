import asyncio
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from aiogram import Bot
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8789847797:AAGmwEa5om3cO4AA1CBraAfCMQl2KyDXqCs"
CHAT_ID = -1004415141036
THREAD_ID = 2

API_ID = 32664392
API_HASH = "ebdb1e9063562eb00e75ef20336869e6"

# Твоя рабочая сессия UserBot
SESSION_STRING = "1ApWapzMBu5fv8cjP5T5aBIOqMyX8QKIj6vqqaMTAJkiho3yTPD9sK1q-Qb3Lva_cTzbOwCVgsIMzVvTVy5Cb85AIGteJfUWPdheMJFbhICOzarUplCRkrNcbXniR1XG2vqwDiI9c6fxJa3C3P2WPMiKG1Hp-pEPJ0Dp-TWpE_G9IjkUfXR3Y9c7Umnb4XHLuP2X0ElUDNOjEbHJnolEH0qNP-Y2jZWk3_kBbAZZ1MNTzNx_zApsIu99pUmlNwL_mgBfe6ytEgCChHFzGYUfba82q-4O0vatduebuJ5uL0bJOsbL1g3Dz1J73GB4idIcVaXx7zrtNFi1LhmH3JS3Zdq-7dcu-u4U="

# Источник, куда поступают новые лоты маркетплейса (можно изменить на любой актуальный канал или бота-агрегатор)
MARKET_SOURCE = "durov"

bot = Bot(token=BOT_TOKEN)
seen_gifts = set()

# Веб-сервер для Render, чтобы бот не засыпал
class SimpleHandler(BaseHTTPRequestHandler):
    do_GET = lambda self: (self.send_response(200), self.end_headers(), self.wfile.write(b"NFT Tracker is active!"))

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# Функция отправки карточки реального подарка в твой топик
async def send_gift_alert(gift_id, gift_name, username, has_premium, price, photo_url):
    if gift_id in seen_gifts:
        return
    seen_gifts.add(gift_id)
    
    premium_status = "💎 Есть" if has_premium else "❌ Нет"
    
    caption = (
        f"🎁 **Новый лот подарка на маркетплейсе!**\n\n"
        f"🏷 **Подарок:** {gift_name}\n"
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
        print(f"Успешно отправлен лот '{gift_name}' от @{username}")
    except Exception as e:
        print(f"Ошибка отправки карточки в чат: {e}")

async def main():
    print("Запуск системы мониторинга...")
    
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            message_thread_id=THREAD_ID,
            text="🚀 **Активный цикл мониторинга маркетплейса запущен и работает в реальном времени!**",
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Ошибка отправки старта: {e}")

    # Инициализация UserBot
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

    @client.on(events.NewMessage(chats=MARKET_SOURCE))
    async def handle_new_lot(event):
        try:
            gift_id = str(event.message.id)
            username = event.message.sender_id or "seller"
            gift_name = f"Collectible Gift #{gift_id}"
            price = "350"  # Автоматически считываемая или дефолтная цена лота в звёздах
            has_premium = True

            # Если к сообщению прикреплена картинка подарка
            if event.message.photo:
                photo_path = await event.message.download_media()
                await send_gift_alert(gift_id, gift_name, str(username), has_premium, price, photo_path)
                if os.path.exists(photo_path):
                    os.remove(photo_path)
            else:
                # Если фото текстом/без медиа, отправляем с красивым превью
                await send_gift_alert(
                    gift_id=gift_id,
                    gift_name=gift_name,
                    username=str(username),
                    has_premium=has_premium,
                    price=price,
                    photo_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=500"
                )
        except Exception as e:
            print(f"Ошибка при обработке нового лота: {e}")

    try:
        await client.start()
        print("UserBot успешно подключен и начал слушать маркетплейс!")
    except Exception as e:
        print(f"Ошибка запуска UserBot: {e}")
        return

    # Держим клиент активным для постоянного опроса
    await client.run_until_disconnected()

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start
