import requests, json, webbrowser, urllib.parse, os, sys
from dotenv import load_dotenv, set_key

VK_APP_ID = 2685278
REDIRECT_URI = "https://oauth.vk.com/blank.html"

# Шаг 1: Открываем ссылку для получения кода
auth_url = (
    f"https://oauth.vk.com/authorize?"
    f"client_id={VK_APP_ID}&"
    f"display=page&"
    f"redirect_uri={REDIRECT_URI}&"
    f"scope=wall,newsfeed,offline&"
    f"response_type=token&"
    f"v=5.131"
)

print("=" * 60)
print("VK TOKEN GENERATOR")
print("=" * 60)
print()
print("1. Открой эту ссылку в браузере:")
print(f"\n{auth_url}\n")
print("2. Разреши доступ приложению")
print("3. После редиректа скопируй ВЕСЬ URL из адресной строки")
print("   (начинается с https://oauth.vk.com/blank.html#...)")
print()

redirect_url = input("Вставь сюда URL из адресной строки браузера: ").strip()

# Парсим токен из URL (фрагмент #access_token=...)
if "access_token=" in redirect_url:
    fragment = redirect_url.split("#")[1]
    params = dict(urllib.parse.parse_qsl(fragment))
    user_token = params.get("access_token", "")
    
    if user_token:
        print(f"\n✅ Токен получен: {user_token[:20]}...")
        
        # Проверяем токен
        resp = requests.get(
            "https://api.vk.com/method/wall.search",
            params={"q": "test", "access_token": user_token, "v": "5.131", "count": 3},
            timeout=10
        )
        data = resp.json()
        count = data.get("response", {}).get("count", 0)
        print(f"✅ Проверка wall.search: найдено {count} постов")
        
        # Записываем в .env
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        set_key(env_path, "VK_TOKEN", user_token)
        print(f"✅ Токен сохранён в .env")
    else:
        print("❌ Не удалось извлечь токен из URL")
else:
    print("❌ В URL не найден access_token")
