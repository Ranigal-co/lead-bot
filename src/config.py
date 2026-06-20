import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
PHOTOGRAPHER_CHAT_ID = int(os.getenv("PHOTOGRAPHER_CHAT_ID", 0))

KEYWORDS = [kw.strip().lower() for kw in os.getenv("KEYWORDS", "").split(",") if kw.strip()]
CITIES = [c.strip().lower() for c in os.getenv("CITIES", "").split(",") if c.strip()]
SEARCH_INTERVAL = int(os.getenv("SEARCH_INTERVAL", "300"))
