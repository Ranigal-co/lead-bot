from datetime import datetime, timezone

from src.config import API_ID, API_HASH, PHONE_NUMBER, MOCK_MODE, KEYWORDS, CITIES

client = None

if not MOCK_MODE:
    from telethon import TelegramClient
    client = TelegramClient("data/telethon_session", API_ID, API_HASH)


async def search_messages(keyword: str, limit: int = 20):
    if MOCK_MODE:
        return _mock_search(keyword, limit)
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


def _mock_search(keyword: str, limit: int = 20):
    import random
    results = []
    templates = [
        f"Ищу {keyword} в {CITIES[0] if CITIES else 'городе'}, недорого, срочно",
        f"Посоветуйте хорошего {keyword} в {CITIES[-1] if CITIES else 'Москве'}",
        f"Кто может провести {keyword} в {CITIES[0] if CITIES else 'Казани'}? Цена договорная",
        f"Продаю фотоаппарат, может нужен {keyword}?",
        f"Свадьба в {CITIES[0] if CITIES else 'СПб'}, ищем {keyword}",
        f"Добрый день! Ищем {keyword} в {CITIES[-1] if CITIES else 'Москве'} на завтра",
        f"Нужен {keyword} для Love Story в центре {CITIES[0] if CITIES else 'Москвы'}",
    ]
    for i in range(min(limit, len(templates))):
        text = templates[i % len(templates)]
        results.append({
            "id": random.randint(10000, 99999),
            "text": text,
            "chat_id": -1001234567890,
            "chat_title": f"Тестовый канал #{i + 1}",
            "date": datetime.now(timezone.utc).isoformat(),
        })
    return results


async def start_client():
    if MOCK_MODE:
        print("Демо-режим: Telethon отключён, используются тестовые данные")
        return
    await client.start(phone=PHONE_NUMBER)
    print("Telethon client started")


async def stop_client():
    if MOCK_MODE:
        return
    await client.disconnect()
    print("Telethon client stopped")
