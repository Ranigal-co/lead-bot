import json
import logging

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        from gigachat import GigaChat
        from src.config import GIGACHAT_CREDENTIALS
        _client = GigaChat(
            credentials=GIGACHAT_CREDENTIALS,
        )
    return _client


async def verify(text: str) -> bool:
    """
    Проверяет текст через GigaChat: является ли пост реальным заказом
    для фотографа/видеографа, а не рекламой или нерелевантным объявлением.
    Возвращает True (лид) или False (не лид).
    """
    try:
        client = _get_client()
    except Exception as e:
        logger.warning(f"Не удалось создать GigaChat клиент: {e}")
        return True  # fallback — пропускаем

    prompt = (
        "Ты — фильтр для Telegram-бота фотографа. "
        "Определи, является ли этот пост реальным заказом от клиента, "
        "который ищет фотографа или видеографа (свадьба, фотосессия, съёмка). "
        "Если это реклама, продвижение, кастинг моделей, "
        "обучение, вакансия НЕ для фотографа — ответь НЕТ.\n\n"
        f"Текст поста:\n{text[:1500]}"
    )

    messages = [
        {
            "role": "system",
            "content": (
                "Ты классифицируешь тексты на русском. "
                "Отвечай строго одним словом: ДА или НЕТ."
            ),
        },
        {"role": "user", "content": prompt},
    ]

    try:
        resp = await client.achat({"messages": messages})
        answer = resp.choices[0].message.content.strip().lower()
        is_lead = answer == "да"
        logger.info(f"GigaChat: {'ЛИД' if is_lead else 'НЕ ЛИД'} — {answer}")
        return is_lead
    except Exception as e:
        logger.error(f"Ошибка GigaChat: {e}", exc_info=True)
        return True  # fallback — пропускаем
