import asyncio
from aiogram import Bot

# Твой токен и данные темы
BOT_TOKEN = "8789847797:AAGmwEa5om3cO4AA1CBraAfCMQl2KyDXqCs"
CHAT_ID = -1004415141036
THREAD_ID = 2

bot = Bot(token=BOT_TOKEN)

async def main():
    print("Fast NFT Tracker запущен...")
    
    # Отправляем тестовое сообщение прямо в тему NFT Tracker
    await bot.send_message(
        chat_id=CHAT_ID,
        message_thread_id=THREAD_ID,
        text="🚀 **Fast NFT Tracker успешно подключен!**\n\nТестовое уведомление доставлено в этот топик.",
        parse_mode="Markdown"
    )

if __name__ == "__main__":
    asyncio.run(main())
