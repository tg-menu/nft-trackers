import asyncio
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from aiogram import Bot
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.payments import GetStarGiftsRequest, GetResaleStarGiftsRequest

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8789847797:AAGmwEa5om3cO4AA1CBraAfCMQl2KyDXqCs"
CHAT_ID = -1004415141036
THREAD_ID = 2

API_ID = 32664392
API_HASH = "ebdb1e9063562eb00e75ef20336869e6"

SESSION_STRING = "1ApWapzMBu5fv8cjP5T5aBIOqMyX8QKIj6vqqaMTAJkiho3yTPD9sK1q-Qb3Lva_cTzbOwCVgsIMzVvTVy5Cb85AIGteJfUWPdheMJFbhICOzarUplCRkrNcbXniR1XG2vqwDiI9c6fxJa3C3P2WPMiKG1Hp-pEPJ0Dp-TWpE_G9IjkUfXR3Y9c7Umnb4XHLuP2X0ElUDNOjEbHJnolEH0qNP-Y2jZWk3_kBbAZZ1MNTzNx_zApsIu99pUmlNwL_mgBfe6ytEgCChHFzGYUfba82q-4O0vatduebuJ5uL0bJOsbL1g3Dz1J73GB4idIcVaXx7zrtNFi1LhmH3JS3Zdq-7dcu-u4U="

bot = Bot(token=BOT_TOKEN)
seen_gifts = set()

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Native Gift Market Monitor is active!")
    def log_message(self, format, *args):
        pass

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

async def send_gift_alert(gift_slug, gift_name, username, owner_name, price):
    if gift_slug in seen_gifts:
        return
    seen_gifts.add(gift_slug)
    
    if len(seen_gifts) > 5000:
        seen_gifts.clear()
        
    user_link = f"@{username}" if username else f"ID: {owner_name}"
    
    caption = (
        f"🚨 **Новый лот в официальном маркете!**\n\n"
        f"🎁 **Подарок:** {gift_name}\n"
        f"👤 **Продавец:** {user_link} ({owner_name})\n"
        f"💰 **Цена:** `{price}` Stars\n"
        f"🔗 **Slug / Ссылка:** `{gift_slug}`"
    )
    
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            message_thread_id=THREAD_ID,
            text=caption,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        print(f"Отправлен лот '{gift_name}' за {price} звезд")
    except Exception as e:
        print(f"Ошибка отправки в чат: {e}")

async def monitor_marketplace():
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    
    await client.start()
    print("UserBot подключен к официальному API подарков Telegram!")

    while True:
        try:
            # 1. Получаем актуальный список всех базовых подарков из маркета
            catalog = await client(GetStarGiftsRequest(hash=0))
            gift_ids = [g.id for g in catalog.gifts if hasattr(g, 'id')]
            
            # 2. Проходим по каждому реальному ID коллекции
            for gift_id in gift_ids:
                try:
                    result = await client(GetResaleStarGiftsRequest(
                        gift_id=gift_id,
                        limit=10,
                        offset="",
                        stars_only=True
                    ))
                    
                    if hasattr(result, 'gifts') and result.gifts:
                        users_dict = {u.id: u for u in getattr(result, 'users', [])}
                        
                        for gift in result.gifts:
                            gift_slug = getattr(gift, 'slug', None)
                            if not gift_slug or gift_slug in seen_gifts:
                                continue
                            
                            # Название подарка (если есть в каталоге)
                            gift_name = f"Подарок ID {gift_id}"
                            for g_obj in catalog.gifts:
                                if g_obj.id == gift_id and hasattr(g_obj, 'title'):
                                    gift_name = g_obj.title
                                    break
                                    
                            if hasattr(gift, 'num') and gift.num:
                                gift_name += f" (№{gift.num})"
                            
                            price = getattr(gift, 'resell_stars', getattr(gift, 'price', 0))
                            owner_id = getattr(gift, 'owner_id', None)
                            username = None
                            owner_name = "Владелец"
                            
                            if owner_id and owner_id in users_dict:
                                u_obj = users_dict[owner_id]
                                username = getattr(u_obj, 'username', None)
                                first = getattr(u_obj, 'first_name', '')
                                last = getattr(u_obj, 'last_name', '')
                                owner_name = f"{first} {last}".strip()

                            await send_gift_alert(
                                gift_slug=gift_slug,
                                gift_name=gift_name,
                                username=username,
                                owner_name=owner_name,
                                price=price
                            )
                except Exception:
                    pass
                
                await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Ошибка получения каталога подарков: {e}")
            await asyncio.sleep(10)
            
        await asyncio.sleep(15)

async def main():
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            message_thread_id=THREAD_ID,
            text="🚀 **Монитор официального маркета подарков запущен!**",
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Не удалось отправить стартовое сообщение: {e}")

    while True:
        try:
            await monitor_marketplace()
        except Exception as e:
            print(f"Сбой клиента, переподключение через 10 секунд: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
