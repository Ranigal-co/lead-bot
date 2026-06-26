import asyncio
import logging

from src.config import (
    KEYWORDS, CITIES, SEARCH_INTERVAL,
    TG_CHANNELS, VK_TOKEN, AI_FILTER_ENABLED,
)
from src.filter import is_lead
from src.database import is_duplicate, save_message
from src.notifier import send_lead
from src.tg_web import get_recent_posts
from src.vk_search import search_vk_posts
from src.heuristics import classify as h_classify, LEAD, NOT_LEAD, UNCERTAIN
from src.ai_filter import verify as ai_verify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Счётчики для статистики
stats = {"skipped_keyword": 0, "skipped_heuristic": 0, "skipped_ai": 0, "sent": 0}


async def process_post(post: dict, source_label: str):
    """Общая обработка одного поста: фильтр -> эвристики -> AI -> отправка."""
    text = post["text"]

    # 1. Ключевые слова + город
    if not is_lead(text):
        stats["skipped_keyword"] += 1
        return

    # 2. Эвристики
    h_result = h_classify(text)
    if h_result == NOT_LEAD:
        stats["skipped_heuristic"] += 1
        logger.info(f"[Эвристики] Пропущен (НЕ ЛИД): {text[:60]}...")
        return

    # 3. AI-верификация (только если UNCERTAIN и AI включён)
    if h_result == UNCERTAIN and AI_FILTER_ENABLED:
        logger.info(f"[AI] Проверяю: {text[:60]}...")
        is_real = await ai_verify(text)
        if not is_real:
            stats["skipped_ai"] += 1
            logger.info("[AI] Пост отклонён AI")
            return

    # 4. Дедупликация
    if is_duplicate(post["id"], post["chat_id"]):
        return

    # 5. Отправка
    logger.info(f"Новый лид! {post['chat_title']}: {text[:100]}...")
    await send_lead(text, post["chat_title"], post["date"])
    save_message(post["id"], post["chat_id"])
    stats["sent"] += 1
    await asyncio.sleep(2)


async def process_tg_channels():
    """Обрабатывает посты из Telegram-каналов."""
    if not TG_CHANNELS:
        return

    for channel in TG_CHANNELS:
        logger.info(f"Проверяем Telegram-канал: t.me/s/{channel}")
        posts = get_recent_posts(channel, limit=10)
        for post in posts:
            await process_post(post, f"t.me/{channel}")


async def process_vk_search():
    """Ищет и обрабатывает посты во ВКонтакте."""
    search_queries = []
    if CITIES:
        for kw in KEYWORDS:
            for city in CITIES:
                search_queries.append(f"{kw} {city}")
    else:
        search_queries = KEYWORDS

    if not search_queries:
        return

    for query in search_queries:
        logger.info(f"Ищем во ВКонтакте по запросу: '{query}'")
        posts = search_vk_posts(query, limit=10)
        for post in posts:
            await process_post(post, "ВКонтакте")
        await asyncio.sleep(3)


async def main_loop():
    logger.info("Бот запущен: VK + Telegram Web + AI фильтрация!")
    if not VK_TOKEN:
        logger.warning("VK_TOKEN не настроен. Демо-режим для ВКонтакте!")
    if AI_FILTER_ENABLED:
        logger.info("AI-фильтрация включена (GigaChat)")
    else:
        logger.info("AI-фильтрация отключена. Работают только эвристики.")

    try:
        while True:
            await process_tg_channels()
            await process_vk_search()

            logger.info(
                "Статистика цикла: "
                f"пропущено(ключи)={stats['skipped_keyword']}, "
                f"пропущено(эвристики)={stats['skipped_heuristic']}, "
                f"пропущено(AI)={stats['skipped_ai']}, "
                f"отправлено={stats['sent']}"
            )
            logger.info(f"Следующий запуск через {SEARCH_INTERVAL}с")
            await asyncio.sleep(SEARCH_INTERVAL)
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main_loop())
