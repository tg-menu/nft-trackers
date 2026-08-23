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

# Твоя сессия UserBot
SESSION_STRING = "1ApWapzMBu5fv8cjP5T5aBIOqMyX8QKIj6vqqaMTAJkiho3yTPD9sK1q-Qb3Lva_cTzbOwCVgsIMzVvTVy5Cb85AIGteJfUWPdheMJFbhICOzarUplCRkrNcbXniR1XG2vqwDiI9c6fxJa3C3P2WPMiKG1Hp-pEPJ0Dp-TWpE_G9IjkUfXR3Y9c7Umnb4XHLuP2X0ElUDNOjEbHJnolEH0qNP-Y2jZWk3_kBbAZZ1MNTzNx_zApsIu99pUmlNwL_mgBfe6ytEgCChHFzGYUfba82q-4O0vatduebuJ5uL0bJOsbL1g3Dz1J73GB4idIcVaXx7zrtNFi1LhmH3JS3Zdq-7dcu-u4U="

bot = Bot(token=BOT_TOKEN)
seen_gifts = set()

# Веб-сервер для Render, чтобы приложение не засыпало
class SimpleHandler(BaseHTTPRequestHandler):
    do_GET = lambda self: (self.send_response(200), self.end_headers(), self.wfile.write(b"NFT Marketplace Bot is active!"))

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

async def send_gift_alert(gift_slug, gift_name, username, has_premium, price, photo_url):
    if gift_slug in seen_gifts:
        return
    seen_gifts.add(gift_slug)
    
    premium_status = "💎 Есть" if has_premium else "❌ Нет"
    
    caption = (
        f"🎁 **Новый лот NFT подарка на маркете!**\n\n"
        f"🏷 **Подарок:** {gift_name}\n"
        f"👤 **Продавец:** @{username} ([Написать связаться](https://t.me/{username}))\n"
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
        print(f"Отправлен реальный лот '{gift_name}' от @{username} за {price} звезд")
    except Exception as e:
        print(f"Ошибка отправки карточки в чат: {e}")

async def monitor_marketplace():
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    
    try:
        await client.start()
        print("UserBot успешно подключен через MTProto API для сканирования маркетплейса подарков!")
    except Exception as e:
        print(f"Ошибка подключения UserBot: {e}")
        return

    # Базовые ID коллекционных подарков для опроса рынка (можно дополнять)
    base_gift_ids = [1, 2, 3, 10, 15, 20, 25, 30]

    while True:
        try:
            for base_id in base_gift_ids:
                # Запрос актуальных выставленных на продажу лотов напрямую из базы Telegram
                result = await client(GetResaleStarGiftsRequest(
                    gift_id=base_id,
                    limit=20
                ))
                
                if hasattr(result, 'gifts'):
                    for gift in result.gifts:
                        gift_slug = getattr(gift, 'slug', str(getattr(gift, 'id', '')))
                        if not gift_slug or gift_slug in seen_gifts:
                            continue
                        
                        gift_name = getattr(gift, 'title', f"Collectible Gift #{base_id}")
                        price = str(getattr(gift, 'resell_price', 'Уточняется'))
                        
                        seller_id = getattr(gift, 'owner_id', None)
                        username = "seller"
                        has_premium = False
                        
                        if seller_id:
                            try:
                                user_entity = await client.get_entity(seller_id)
                                if getattr(user_entity, 'username', None):
                                    username = user_entity.username
                                has_premium = getattr(user_entity, 'premium', False)
                            except:
                                pass

                        # Базовое превью или фото подарка с маркета
                        photo_url = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=500"

                        await send_gift_alert(
                            gift_slug=gift_slug,
                            gift_name=gift_name,
                            username=username,
                            has_premium=has_premium,
                            price=price,
                            photo_url=photo_url
                        )
                
                await asyncio.sleep(2)
        except Exception as e:
            print(f"Ошибка в цикле сканирования маркета: {e}")
            
        await asyncio.sleep(10)

async def main():
    print("Запуск системы мониторинга рынка...")
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            message_thread_id=THREAD_ID,
            text="🚀 **Мониторинг реального маркетплейса подарков запущен и работает!**",
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Ошибка отправки старта: {e}")

    asyncio.create_task(monitor_marketplace())

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    asyncio.run(main())
