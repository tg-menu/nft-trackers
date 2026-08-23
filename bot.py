import asyncio
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from aiogram import Bot

BOT_TOKEN = "8789847797:AAGmwEa5om3cO4AA1CBraAfCMQl2KyDXqCs"
CHAT_ID = -1004415141036
THREAD_ID = 2

bot = Bot(token=BOT_TOKEN)

# Множество для хранения ID уже отправленных подарков (чтобы не спамить дубликатами)
seen_gifts = set()

# Простой веб-сервер для Render, чтобы сервис не засыпал
class SimpleHandler(BaseHTTPRequestHandler):
    do_GET = lambda self: (self.send_response(200), self.end_headers(), self.wfile.write(b"NFT Tracker is active!"))

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# Функция отправки карточки подарка в топик
async def send_gift_alert(gift_id, username, has_premium, price, photo_url):
    if gift_id in seen_gifts:
        return  # Если уже отправляли этот подарок, пропускаем
    
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
        print(f"Ошибка отправки фото: {e}")

# Функция-монтиторинг (здесь будет твой парсер / запрос к API маркетплейса)
async def market_checker():
    while True:
        try:
            # ТУТ БУДЕТ ЗАПРОС К МАРКЕТПЛЕЙСУ ИЛИ ПАРСЕРУ
            # Пример фейковых данных для теста:
            # new_gifts = fetch_from_marketplace()
            
            # Для примера имитируем появление нового подарка:
            # await send_gift_alert("gift_12345", "titan390", True, "15 TON", "https://via.placeholder.com/300")
            
            pass
        except Exception as e:
            print(f"Ошибка в цикле мониторинга: {e}")
            
        await asyncio.sleep(10)  # Проверять каждые 10 секунд

async def main():
    print("Fast NFT Tracker запущен и следит за маркетплейсом...")
    
    # Запускаем фоновый цикл мониторинга рынка
    asyncio.create_task(market_checker())

    # Бесконечный цикл, чтобы бот не выключался
    while True:
        await asyncio.sleep(3600)

if __name__ == "__4__main__" or True: # Запуск сервера и бота
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    asyncio.run(main())
