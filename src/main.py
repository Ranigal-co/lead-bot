import asyncio
import logging

from src.config import KEYWORDS, CITIES, SEARCH_INTERVAL, TG_CHANNELS, VK_TOKEN
from src.filter import is_lead
from src.database import is_duplicate, save_message
from src.notifier import send_lead
from src.tg_web import get_recent_posts
from src.vk_search import search_vk_posts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def process_tg_channels():
    """Fetches and processes recent posts from public Telegram channels."""
    if not TG_CHANNELS:
        logger.info("Нет Telegram-каналов для мониторинга в TG_CHANNELS")
        return

    logger.info(f"Начинаем проверку Telegram-каналов: {', '.join(TG_CHANNELS)}")
    for channel in TG_CHANNELS:
        logger.info(f"Проверяем Telegram-канал: t.me/s/{channel}")
        posts = get_recent_posts(channel, limit=10)

        for post in posts:
            text = post["text"]
            if not is_lead(text):
                continue
            if is_duplicate(post["id"], post["chat_id"]):
                continue

            logger.info(f"Новый лид в Telegram! {post['chat_title']}: {text[:100]}...")
            await send_lead(text, post["chat_title"], post["date"])
            save_message(post["id"], post["chat_id"])
            await asyncio.sleep(2)


async def process_vk_search():
    """Searches VK for photographer-related leads using keywords + cities."""
    logger.info("Начинаем поиск во ВКонтакте...")

    # We search VK using combinations of keyword + city for targeted results
    search_queries = []
    if CITIES:
        for kw in KEYWORDS:
            for city in CITIES:
                search_queries.append(f"{kw} {city}")
    else:
        search_queries = KEYWORDS

    if not search_queries:
        logger.info("Нет ключевых слов для поиска в VK")
        return

    # To avoid hitting VK API rate limits too quickly, we limit the number of queries per run
    # and add a small delay between requests
    for query in search_queries:
        logger.info(f"Ищем во ВКонтакте по запросу: '{query}'")
        posts = search_vk_posts(query, limit=10)

        for post in posts:
            text = post["text"]
            if not is_lead(text):
                continue
            if is_duplicate(post["id"], post["chat_id"]):
                continue

            logger.info(f"Новый лид во ВКонтакте! {post['chat_title']}: {text[:100]}...")
            await send_lead(text, post["chat_title"], post["date"])
            save_message(post["id"], post["chat_id"])
            await asyncio.sleep(2)

        await asyncio.sleep(3)  # Respect VK API rate limits


async def main_loop():
    logger.info("Бот запущен в режиме VK + Telegram Web!")
    if not VK_TOKEN:
        logger.warning("VK_TOKEN не настроен. Для ВКонтакте используется демонстрационный режим!")

    try:
        while True:
            # 1. Process Telegram channels
            try:
                await process_tg_channels()
            except Exception as e:
                logger.error(f"Ошибка при обработке Telegram-каналов: {e}", exc_info=True)

            # 2. Process VK Search
            try:
                await process_vk_search()
            except Exception as e:
                logger.error(f"Ошибка при обработке поиска во ВКонтакте: {e}", exc_info=True)

            logger.info(f"Цикл завершён. Следующий запуск через {SEARCH_INTERVAL}с")
            await asyncio.sleep(SEARCH_INTERVAL)
    except Exception as e:
        logger.critical(f"Критическая ошибка в главном цикле: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main_loop())
