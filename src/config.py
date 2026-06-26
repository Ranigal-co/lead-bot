import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
PHOTOGRAPHER_CHAT_ID = int(os.getenv("PHOTOGRAPHER_CHAT_ID", 0))

KEYWORDS = [kw.strip().lower() for kw in os.getenv("KEYWORDS", "").split(",") if kw.strip()]
VK_KEYWORDS = [kw.strip().lower() for kw in os.getenv("VK_KEYWORDS", "").split(",") if kw.strip()]
CITIES = [c.strip().lower() for c in os.getenv("CITIES", "").split(",") if c.strip()]
SEARCH_INTERVAL = int(os.getenv("SEARCH_INTERVAL", "300"))

MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"

VK_TOKEN = os.getenv("VK_TOKEN")
TG_CHANNELS = [ch.strip() for ch in os.getenv("TG_CHANNELS", "").split(",") if ch.strip()]

GIGACHAT_CREDENTIALS = os.getenv("GIGACHAT_CREDENTIALS", "")
AI_FILTER_ENABLED = os.getenv("AI_FILTER_ENABLED", "false").lower() == "true"
