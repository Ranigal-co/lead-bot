from src.config import KEYWORDS, CITIES


def get_city_stem(city: str) -> str:
    city = city.lower().strip()
    # Strip common Russian noun endings to match declensions (e.g. Москва -> москв)
    if len(city) > 3:
        if city[-1] in ["а", "я", "е", "и", "ь", "у", "ы"]:
            return city[:-1]
    return city


def contains_keyword(text: str) -> bool:
    text_lower = text.lower()
    for kw in KEYWORDS:
        if kw in text_lower:
            return True
    return False


def contains_city(text: str) -> bool:
    text_lower = text.lower()
    for city in CITIES:
        stem = get_city_stem(city)
        if stem in text_lower:
            return True
    return False


def is_lead(text: str) -> bool:
    return contains_keyword(text) and contains_city(text)
