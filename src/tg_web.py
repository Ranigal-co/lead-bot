import hashlib
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone


def string_to_int(s: str) -> int:
    """Converts a string (like channel name) into a unique 64-bit integer for DB storage."""
    return int(hashlib.md5(s.encode()).hexdigest()[:15], 16)


def get_recent_posts(channel_name: str, limit: int = 10):
    """Fetches recent posts from a public Telegram channel via t.me/s/ web interface."""
    url = f"https://t.me/s/{channel_name}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching channel {channel_name}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    messages = soup.find_all("div", class_="tgme_widget_message")

    results = []
    chat_id = string_to_int(channel_name)

    # We want the most recent ones first, so reverse or slice from the end
    for msg in messages[-limit:]:
        data_post = msg.get("data-post")
        if not data_post or "/" not in data_post:
            continue

        try:
            post_id = int(data_post.split("/")[-1])
        except ValueError:
            continue

        text_elem = msg.find("div", class_="tgme_widget_message_text")
        if not text_elem:
            continue

        text = text_elem.get_text(separator="\n").strip()

        time_elem = msg.find("time", class_="time")
        if time_elem and time_elem.get("datetime"):
            date_str = time_elem.get("datetime")
        else:
            date_str = datetime.now(timezone.utc).isoformat()

        # Add link to original post for photographer's convenience
        post_link = f"https://t.me/{data_post}"
        full_text = f"{text}\n\n🔗 Ссылка: {post_link}"

        results.append({
            "id": post_id,
            "text": full_text,
            "chat_id": chat_id,
            "chat_title": f"t.me/{channel_name}",
            "date": date_str,
        })

    return results
