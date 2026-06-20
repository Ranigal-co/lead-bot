import asyncio
import logging

from src.config import KEYWORDS, SEARCH_INTERVAL
from src.search import client, search_messages, start_client, stop_client
from src.filter import is_lead
from src.database import is_duplicate, save_message
from src.notifier import send_lead

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def process_keyword(keyword: str):
    messages = await search_messages(keyword, limit=10)
    for msg in messages:
        text = msg["text"]
        if not is_lead(text):
            continue
        if is_duplicate(msg["id"], msg["chat_id"]):
            continue
        logger.info(f"Новый лид! {msg['chat_title']}: {text[:100]}")
        await send_lead(text, msg["chat_title"], msg["date"])
        save_message(msg["id"], msg["chat_id"])
        await asyncio.sleep(2)


async def main_loop():
    await start_client()
    logger.info("Бот запущен и начинает поиск...")
    try:
        while True:
            for kw in KEYWORDS:
                logger.info(f"Ищем: {kw}")
                await process_keyword(kw)
                await asyncio.sleep(5)
            logger.info(f"Цикл завершён. Следующий через {SEARCH_INTERVAL}с")
            await asyncio.sleep(SEARCH_INTERVAL)
    finally:
        await stop_client()


if __name__ == "__main__":
    asyncio.run(main_loop())
