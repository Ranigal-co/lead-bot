from aiogram import Bot
from src.config import BOT_TOKEN, PHOTOGRAPHER_CHAT_ID

bot = Bot(token=BOT_TOKEN)


async def send_lead(lead_text: str, chat_title: str, date: str):
    message = (
        f"Найден потенциальный лид!\n\n"
        f"Источник: {chat_title}\n"
        f"Дата: {date}\n"
        f"---\n{lead_text}\n---"
    )
    await bot.send_message(PHOTOGRAPHER_CHAT_ID, message)
