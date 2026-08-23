import asyncio
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from aiogram import Bot
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.payments import GetResaleStarGiftsRequest

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
    do_GET = lambda self: (self.send_response(200), self.end_headers(), self.wfile.write(b"Real Gift Marketplace Monitor is active!"))

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

async def send_gift_alert(gift_slug, gift_name, username, owner_name, price):
    if gift_slug in seen_gifts:
        return
    seen_gifts.add(gift_slug)
    
    # Ограничение памяти для кэша виденных подарков (чтобы не раздувать ОЗУ)
    if len(seen_gifts) > 5000:
        seen_gifts.clear()
        
    user_link = f"@{username}" if username else f"[Пользователь (ID)](https://t.me/{username})" if username else "Скрыт"
    
    caption = (
        f"🚨 **Новый лот подарка на маркете!**\n\n"
        f"🏷 **Подарок:** {gift_name}\n"
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
        print(f"Отправлен реальный лот '{gift_name}' от @{username} за {price} звезд")
    except Exception as e:
        print(f"Ошибка отправки в чат: {e}")

async def monitor_marketplace():
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    
    try:
        await client.start()
        print("UserBot успешно подключен через MTProto API к рынку подарков!")
    except Exception as e:
        print(f"Ошибка подключения UserBot: {e}")
        return

    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            message_thread_id=THREAD_ID,
            text="🚀 **Мониторинг реального рынка подарков запущен!**",
            parse_mode="Markdown"
        )
    except:
        pass

    # Базовые ID подарков для сканирования рынка перепродажи
    # (Telegram группирует коллекционные подарки по базовым ID исходных гифтов)
    base_gift_ids = list(range(1, 100))

    while True:
        try:
            for base_id in base_gift_ids:
                try:
                    result = await client(GetResaleStarGiftsRequest(
                        gift_id=base_id,
                        limit=20,
                        offset="",
                        stars_only=True
                    ))
                    
                    if hasattr(result, 'gifts') and result.gifts:
                        # Собираем словарь пользователей для быстрого сопоставления ID владельца с юзернеймом
                        users_dict = {u.id: u for u in getattr(result, 'users', [])}
                        
                        for gift in result.gifts:
                            gift_slug = getattr(gift, 'slug', None)
                            if not gift_slug or gift_slug in seen_gifts:
                                continue
                            
                            gift_name = f"Collectible Gift #{base_id}"
                            if hasattr(gift, 'num') and gift.num:
                                gift_name = f"Gift #{base_id} (№{gift.num})"
                            
                            # Цена в звездах
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
                    # Если по данному ID нет активных торгов или метод временно недоступен — идем дальше
                    pass
                
                await asyncio.sleep(0.3)
        except Exception as e:
            print(f"Ошибка в цикле сканирования маркета: {e}")
            
        # Пауза перед следующим полным циклом мониторинга рынка
        await asyncio.sleep(10)

async def main():
    asyncio.create_task(monitor_marketplace())
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    asyncio.run(main())
