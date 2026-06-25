import requests
from datetime import datetime, timezone
import random
from src.config import VK_TOKEN, CITIES, KEYWORDS


def search_vk_posts(keyword: str, limit: int = 10):
    """Searches public posts on VK using newsfeed.search API."""
    if not VK_TOKEN:
        return _mock_vk_search(keyword, limit)

    url = "https://api.vk.com/method/newsfeed.search"
    params = {
        "q": keyword,
        "access_token": VK_TOKEN,
        "v": "5.131",
        "count": limit,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if "error" in data:
            print(f"VK API Error: {data['error']['error_msg']}")
            return []

        items = data.get("response", {}).get("items", [])
        results = []

        for item in items:
            post_id = item.get("id")
            owner_id = item.get("owner_id")
            text = item.get("text", "")
            date_timestamp = item.get("date")

            if not text or post_id is None or owner_id is None:
                continue

            # Format the date
            if date_timestamp:
                date_str = datetime.fromtimestamp(date_timestamp, timezone.utc).isoformat()
            else:
                date_str = datetime.now(timezone.utc).isoformat()

            # Append post link
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
        print(f"Error fetching VK posts: {e}")
        return []


def _mock_vk_search(keyword: str, limit: int = 10):
    """Generates mock VK search results if VK_TOKEN is not configured."""
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
        owner_id = -random.randint(100000, 999999)  # negative for community walls

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
