import requests
from datetime import datetime, timezone
import random
import logging
from src.config import VK_TOKEN, CITIES, KEYWORDS

logger = logging.getLogger(__name__)

# Cache: do we have a working token?
_token_tested = False
_token_works = False


def _test_token():
    """Проверяет, работает ли VK токен для поиска."""
    global _token_tested, _token_works
    if _token_tested:
        return _token_works

    _token_tested = True
    if not VK_TOKEN:
        logger.warning("VK_TOKEN не настроен. Используется демо-режим.")
        return False

    # Проверяем через newsfeed.search (простой запрос)
    for method in ["newsfeed.search", "wall.search"]:
        try:
            resp = requests.get(
                f"https://api.vk.com/method/{method}",
                params={"q": "test", "access_token": VK_TOKEN, "v": "5.131", "count": 1},
                timeout=5,
            )
            data = resp.json()
            if "error" not in data:
                count = data.get("response", {}).get("count", 0)
                if count > 0:
                    _token_works = True
                    logger.info(f"VK токен работает (метод {method})")
                    return True
        except Exception:
            continue

    logger.warning(
        "VK токен не работает для поиска. "
        "Нужен user access token с правами wall,newsfeed,offline.\n"
        "Запустите: python get_vk_token.py"
    )
    return False


def search_vk_posts(keyword: str, limit: int = 10):
    """Searches public posts on VK using wall.search API."""
    if not _test_token():
        return _mock_vk_search(keyword, limit)

    # Пробуем wall.search (лучше работает с сервисными токенами)
    for method in ["wall.search", "newsfeed.search"]:
        params = {
            "q": keyword,
            "access_token": VK_TOKEN,
            "v": "5.131",
            "count": limit,
        }
        if method == "wall.search":
            params["owners_only"] = 0

        try:
            response = requests.get(f"https://api.vk.com/method/{method}", params=params, timeout=10)
            data = response.json()

            if "error" in data:
                logger.debug(f"VK {method} error: {data['error']['error_msg']}")
                continue

            items = data.get("response", {}).get("items", [])
            if not items:
                continue

            results = []
            for item in items:
                post_id = item.get("id")
                owner_id = item.get("owner_id")
                text = item.get("text", "")
                date_timestamp = item.get("date")

                if not text or post_id is None or owner_id is None:
                    continue

                if date_timestamp:
                    date_str = datetime.fromtimestamp(date_timestamp, timezone.utc).isoformat()
                else:
                    date_str = datetime.now(timezone.utc).isoformat()

                post_link = f"https://vk.com/wall{owner_id}_{post_id}"
                full_text = f"{text}\n\n🔗 Ссылка: {post_link}"

                results.append({
                    "id": post_id,
                    "text": full_text,
                    "chat_id": owner_id,
                    "chat_title": "ВКонтакте",
                    "date": date_str,
                })

            return results

        except Exception as e:
            logger.debug(f"VK {method} error: {e}")
            continue

    logger.warning(f"VK API не вернул результатов для '{keyword[:30]}'. Возможно, токен не работает.")
    return []


def _mock_vk_search(keyword: str, limit: int = 10):
    """Generates mock VK search results for demo/testing."""
    results = []
    city = CITIES[0] if CITIES else "Москва"
    templates = [
        f"Ребята, порекомендуйте классного специалиста ({keyword}) в г. {city}. Свадьба в сентябре!",
        f"Ищу {keyword} на свадебный день {city}, пишите в ЛС с портфолио и ценами.",
        f"ВКонтакте: требуется {keyword} для семейной фотосессии в г. {city} на эти выходные.",
    ]

    for i in range(min(limit, len(templates))):
        text = templates[i % len(templates)]
        post_id = random.randint(100000, 999999)
        owner_id = -random.randint(100000, 999999)

        post_link = f"https://vk.com/wall{owner_id}_{post_id}"
        full_text = f"{text}\n\n🔗 Ссылка: {post_link}"

        results.append({
            "id": post_id,
            "text": full_text,
            "chat_id": owner_id,
            "chat_title": "ВКонтакте (Демо)",
            "date": datetime.now(timezone.utc).isoformat(),
        })

    return results
