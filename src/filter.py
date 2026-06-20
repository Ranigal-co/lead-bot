from src.config import KEYWORDS, CITIES


def contains_keyword(text: str) -> bool:
    text_lower = text.lower()
    for kw in KEYWORDS:
        if kw in text_lower:
            return True
    return False


def contains_city(text: str) -> bool:
    text_lower = text.lower()
    for city in CITIES:
        if city in text_lower:
            return True
    return False


def is_lead(text: str) -> bool:
    return contains_keyword(text) and contains_city(text)
