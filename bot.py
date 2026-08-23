import asyncio
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from aiogram import Bot

BOT_TOKEN = "8789847797:AAGmwEa5om3cO4AA1CBraAfCMQl2KyDXqCs"
CHAT_ID = -1004415141036
THREAD_ID = 2

bot = Bot(token=BOT_TOKEN)

# Простой веб-сервер, чтобы Render (Web Service) считал проект живым
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"NFT Tracker is active!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

async def main():
    print("Fast NFT Tracker запущен...")
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            message_thread_id=THREAD_ID,
            text="🚀 **Fast NFT Tracker успешно подключен!**\n\nТестовое уведомление доставлено в этот топик.",
            parse_mode="Markdown"
        )
        print("Сообщение успешно отправлено в тему!")
    except Exception as e:
        print(f"Ошибка при отправке: {e}")

    # Держим процесс активным
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    # Запускаем веб-сервер в фоне для Render
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Запускаем бота
    asyncio.run(main())
