from telethon import TelegramClient
from src.config import API_ID, API_HASH, PHONE_NUMBER

client = TelegramClient("data/telethon_session", API_ID, API_HASH)


async def search_messages(keyword: str, limit: int = 20):
    results = []
    async for message in client.iter_messages(None, search=keyword, limit=limit):
        if not message.text:
            continue
        chat_title = message.chat.title if message.chat else "Личный чат"
        results.append({
            "id": message.id,
            "text": message.text,
            "chat_id": message.chat_id if message.chat else None,
            "chat_title": chat_title,
            "date": message.date.isoformat(),
        })
    return results


async def start_client():
    await client.start(phone=PHONE_NUMBER)
    print("Telethon client started")


async def stop_client():
    await client.disconnect()
    print("Telethon client stopped")
