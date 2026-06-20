# План разработки и развёртывания Telegram-бота для фотографа

> **Роль**: Senior DevOps/Python Engineer-наставник
> **Новичок**: минимальный опыт Python и Linux
> **Цель**: Telegram-бот для поиска лидов по ключевым словам + городу, пересылка фотографу

---

## Этап 0. Подготовка VPS

### 0.1 Первый вход на сервер (SSH)

**Что делаем**: Подключаемся к вашему VPS через SSH. VPS — это удалённый компьютер в дата-центре. SSH — протокол для удалённого управления им.

```bash
# Выполняется на вашем локальном компьютере (в терминале / PowerShell)
ssh root@<IP-адрес-вашего-сервера>
# Например: ssh root@123.45.67.89
```

**Проверка**: После ввода пароля (вам выдал хостинг-провайдер) вы увидите приглашение вида `root@vps:~#`

**Частая ошибка**: Подключение зависает — проверьте, что IP-адрес верный, а в SSH-клиенте не блокируется порт 22 (стандартный порт SSH).

---

### 0.2 Смена пароля root

**Что делаем**: Меняем временный пароль от хостинга на свой надёжный.

```bash
# Выполняется на VPS
passwd
# Система попросит ввести новый пароль дважды
```

**Проверка**: После успешной смены увидите `password updated successfully`.

**Частая ошибка**: Пароль не принимается — используйте минимум 8 символов, с цифрами и буквами разного регистра.

---

### 0.3 Создание non-root пользователя с sudo

**Что делаем**: Создаём обычного пользователя (не root). root — суперадминистратор, через него опасно работать постоянно. sudo позволяет выполнять команды от root временно.

```bash
# Выполняется на VPS
adduser fotobot
# Система попросит ввести пароль и данные (можно нажимать Enter, пропуская)

usermod -aG sudo fotobot
# Добавляем пользователя в группу sudo — даём право выполнять команды через sudo
```

**Проверка**: Выйдите из сессии root (`exit`) и зайдите снова как новый пользователь:
```bash
ssh fotobot@<IP-адрес>
```
Если зашли — всё в порядке.

**Частая ошибка**: Забыли пароль — запишите его сразу.

---

### 0.4 Настройка UFW (Firewall)

**Что делаем**: Включаем фаервол, разрешаем только SSH (порт 22). Всё остальное закрыто.

```bash
# Выполняется на VPS
sudo ufw allow OpenSSH
sudo ufw enable
sudo ufw status
```

**Проверка**: Команда `sudo ufw status` покажет `Status: active` и список разрешённых правил.

**Частая ошибка**: Забыли разрешить SSH перед включением — потеряете доступ к серверу. Поэтому сначала `allow OpenSSH`, потом `enable`.

---

### 0.5 Отключение root-логина по SSH

**Что делаем**: Запрещаем вход для root через SSH. Теперь заходить можно только через пользователя fotobot с sudo.

```bash
# Выполняется на VPS
sudo nano /etc/ssh/sshd_config
```

Найдите строку `#PermitRootLogin yes`, измените на:
```
PermitRootLogin no
```
Сохраните (Ctrl+O, Enter, Ctrl+X).

```bash
sudo systemctl restart sshd
```

**Проверка**: Попробуйте зайти как root — `ssh root@<IP>` — должно отказать с `Permission denied`.

**Частая ошибка**: Не перезапустили SSH-сервис (`systemctl restart sshd`) — изменения не вступят в силу.

---

### 0.6 Установка fail2ban

**Что делаем**: fail2ban автоматически блокирует IP-адреса, с которых多次 вводят неверный пароль. Защита от брутфорса.

```bash
# Выполняется на VPS
sudo apt update
sudo apt install fail2ban -y
sudo systemctl enable fail2ban --now
```

**Проверка**: `sudo fail2ban-client status` покажет статус.

**Частая ошибка**: fail2ban не настроен по умолчанию — этого достаточно для начала, позже можно тонко настроить.

---

### 0.7 Обновление системы

**Что делаем**: Устанавливаем свежие обновления пакетов и ядра — безопасность и исправление багов.

```bash
# Выполняется на VPS
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
```

**Проверка**: Если после `apt update` нет ошибок и `apt upgrade` не показывает пакетов для обновления — готово.

**Частая ошибка**: Пропускают этот шаг, потом ставят Docker на старую систему и получают ошибки совместимости.

---

### 0.8 Установка Docker

**Что делаем**: Устанавливаем Docker через официальный скрипт — самый простой способ.

```bash
# Выполняется на VPS
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

**Проверка**: `docker --version` покажет версию (например, `Docker version 27.0.3`).

**Частая ошибка**: Установка из apt-репозитория Ubuntu — там старая версия. Используем официальный скрипт.

---

### 0.9 Docker без sudo (добавление в группу docker)

**Что делаем**: Чтобы не писать `sudo docker` каждый раз, добавляем пользователя в группу docker.

```bash
# Выполняется на VPS
sudo usermod -aG docker $USER
# Выйдите и зайдите снова, чтобы изменения вступили в силу:
exit
# Заново подключитесь:
ssh fotobot@<IP-адрес>
```

**Проверка**: `docker ps` — если не ругается на права, всё ок.

**Частая ошибка**: Забыли выйти и зайти заново — группа не применяется до перезахода.

---

### 0.10 Установка docker-compose

**Что делаем**: docker-compose — инструмент для запуска нескольких контейнеров одной командой (у нас будет один сервис, но удобно управлять).

```bash
# Выполняется на VPS
sudo apt install docker-compose-plugin -y
```

**Проверка**: `docker compose version` покажет версию.

**Частая ошибка**: Путают старый `docker-compose` (черточка) и новый `docker compose` (пробел). Используем новый — `docker compose`.

---

## Этап 1. Получение учётных данных Telegram

### 1.1 Создание бота через @BotFather

**Что делаем**: BotFather — официальный бот Telegram для создания других ботов. Он даст вам Bot Token — ключ, которым ваш код будет авторизовываться как бот.

**Действия**:
1. Откройте Telegram, найдите @BotFather
2. Напишите `/newbot`
3. Введите имя бота (например, `PhotoLeadFinderBot`)
4. Введите username бота, заканчивающийся на `bot` (например, `PhotoLeadFinderBot`)
5. BotFather пришлёт сообщение с токеном вида: `1234567890:ABCdefGHIjklmNOPqrstUVwxyz`

**Проверка**: У вас есть строка вида `1234567890:ABCdefGHIjklmNOPqrstUVwxyz` — это ваш Bot Token.

**Частая ошибка**: Потеряли токен — просто напишите `/mybots` в @BotFather, найдите бота и нажмите «API Token».

---

### 1.2 Получение api_id и api_hash для Telethon

**Что делаем**: Telethon работает через API Telegram. Для этого нужно зарегистрировать «приложение» на my.telegram.org. Создаём отдельный «технический» аккаунт (не личный номер фотографа), чтобы снизить риски блокировки.

**Действия**:
1. Заведите отдельный номер телефона (можно виртуальный, e.g. через Google Voice или другую eSIM)
2. Зайдите на https://my.telegram.org/auth с этого аккаунта
3. Введите номер телефона, подтвердите код из Telegram
4. Нажмите «API Development tools»
5. Заполните: App title (любое, e.g. `PhotoLeadFinder`), Short name (e.g. `photoleadfinder`), URL (можно оставить пустым), Platform (Desktop)
6. Нажмите «Create application»
7. Скопируйте `api_id` (число) и `api_hash` (строка символов)

**Проверка**: У вас есть три вещи: `api_id`, `api_hash` и номер телефона технического аккаунта.

**Частая ошибка**: Используют личный номер фотографа для парсинга — это опасно, см. следующий шаг.

---

### 1.3 Предупреждение о рисках использования user-аккаунта для парсинга

**⚠️ ВАЖНО**: Telegram запрещает парсинг (автоматический сбор данных) через user-аккаунты в своей Terms of Service. Возможные последствия:
- Временная блокировка аккаунта (от нескольких часов до недели)
- Постоянная блокировка аккаунта
- Блокировка номера телефона (не сможете зарегистрироваться снова)

**Как снизить риски**:
1. Используйте ОТДЕЛЬНЫЙ номер телефона, не личный и не рабочий
2. Не парсите слишком часто (интервал между запросами 5-10+ секунд)
3. Не парсите по ночам (имитируйте активность реального пользователя)
4. Ограничьте количество групп/каналов для поиска (10-20 максимум)
5. Будьте готовы к тому, что аккаунт может быть заблокирован — предусмотрите запасной

**Это не шутка**. Telegram блокирует аккаунты за автоматизированные действия, даже если вы используете официальную библиотеку.

---

## Этап 2. Структура проекта

### 2.1 Дерево директорий проекта

Создаём локально на вашем компьютере (не на VPS):

```
photobot/
├── .env                  # Секреты (токены, api_id, ключевые слова) — НЕ В GIT
├── .gitignore            # Что не попадает в git
├── requirements.txt      # Зависимости Python
├── Dockerfile            # Инструкция для Docker
├── docker-compose.yml    # Конфигурация запуска
├── data/                 # Данные (БД, сессии Telethon)
│   └── .gitkeep          # Пустой файл, чтобы папка попала в git
├── src/
│   ├── __init__.py
│   ├── config.py         # Чтение .env
│   ├── search.py         # Поиск через Telethon
│   ├── filter.py         # Фильтрация по ключевым словам + городу
│   ├── database.py       # Работа с SQLite (дедупликация)
│   ├── notifier.py       # Отправка найденных лидов через бота
│   └── main.py           # Точка входа — запускает всё
```

**Объяснение модулей**:

| Модуль | Назначение |
|--------|-----------|
| `config.py` | Читает `.env` и выдаёт настройки остальным модулям |
| `search.py` | Подключается к Telegram через Telethon, ищет сообщения по ключевым словам |
| `filter.py` | Проверяет, подходит ли сообщение (содержит нужные слова + город) |
| `database.py` | Сохраняет найденные сообщения в SQLite, чтобы не отправлять дубликаты |
| `notifier.py` | Отправляет сообщение фотографу через aiogram-бота |
| `main.py` | Координатор — запускает поиск, передаёт результат в фильтр, потом в БД, потом в уведомление |

**Частая ошибка**: Забывают создать папку `data/` — Telethon не сможет сохранить сессию, и при каждом перезапуске будет просить код авторизации.

---

### 2.2 requirements.txt

```text
aiogram==3.12.0
telethon==1.36.0
SQLAlchemy==2.0.31
python-dotenv==1.0.1
```

**Частая ошибка**: Не фиксируют версии (`aiogram` без `==3.12.0`). Через месяц выйдет новая версия с breaking changes — и бот сломается при пересборке.

---

## Этап 3. Локальная разработка (на вашем компьютере)

### 3.1 Подготовка окружения

**Что делаем**: Убеждаемся, что Python установлен, создаём виртуальное окружение (venv) — изолированный «микромир» для нашего проекта, чтобы зависимости не конфликтовали с другими проектами.

```bash
# Выполняется на вашем локальном компьютере
python --version   # Должно быть 3.10+ Если нет — скачайте с python.org

# Создаём папку проекта
mkdir photobot
cd photobot

# Создаём виртуальное окружение
python -m venv venv

# Активируем:
# Windows (PowerShell):
venv\Scripts\Activate.ps1
# Mac/Linux:
# source venv/bin/activate

# Устанавливаем зависимости:
pip install -r requirements.txt
```

**Проверка**: После `pip install` нет ошибок. Команда `python -c "import aiogram; print(aiogram.__version__)"` работает без ошибок.

**Частая ошибка**: Не активировали venv — устанавливаете пакеты глобально, потом через полгода всё ломается. Всегда проверяйте, что `(venv)` написано в начале строки терминала.

---

### 3.2 config.py — чтение настроек из .env

Создаём файл `.env` в корне проекта:

```env
# .env
BOT_TOKEN=1234567890:ABCdefGHIjklmNOPqrstUVwxyz
API_ID=12345
API_HASH=abcdef1234567890abcdef1234567890
PHONE_NUMBER=+71234567890
PHOTOGRAPHER_CHAT_ID=987654321
KEYWORDS=свадьба,фотосессия,фотограф,портрет,love story,семейная
CITIES=Москва,СПб,Казань,Новосибирск
SEARCH_INTERVAL=300
```

**Что значит каждое поле**:
- `BOT_TOKEN` — из @BotFather
- `API_ID`, `API_HASH` — из my.telegram.org
- `PHONE_NUMBER` — номер технического аккаунта Telegram (с "+" и кодом страны)
- `PHOTOGRAPHER_CHAT_ID` — ID чата фотографа, куда бот будет слать лиды (узнать можно у @userinfobot)
- `KEYWORDS` — через запятую, слова которые ищем в сообщениях
- `CITIES` — через запятую, города для фильтрации
- `SEARCH_INTERVAL` — как часто искать (в секундах). 300 = 5 минут

**Частая ошибка**: `PHOTOGRAPHER_CHAT_ID` может быть отрицательным числом для групп/каналов. Это нормально.

Теперь `src/config.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()  # читает .env

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
PHOTOGRAPHER_CHAT_ID = int(os.getenv("PHOTOGRAPHER_CHAT_ID"))

KEYWORDS = [kw.strip().lower() for kw in os.getenv("KEYWORDS", "").split(",") if kw.strip()]
CITIES = [c.strip().lower() for c in os.getenv("CITIES", "").split(",") if c.strip()]
SEARCH_INTERVAL = int(os.getenv("SEARCH_INTERVAL", "300"))
```

**Проверка**: `python -c "from src.config import KEYWORDS; print(KEYWORDS)"` — должны увидеть список слов.

---

### 3.3 Модуль поиска (search.py)

**Что делаем**: Подключаемся к Telegram через Telethon как user-аккаунт, ищем сообщения по ключевым словам в глобальном поиске.

```python
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import asyncio
from src.config import API_ID, API_HASH, PHONE_NUMBER, KEYWORDS

client = TelegramClient("data/telethon_session", API_ID, API_HASH)

async def search_messages(keyword: str, limit: int = 20):
    """Ищет сообщения по ключевому слову, возвращает список словарей."""
    results = []
    async for message in client.iter_messages(None, search=keyword, limit=limit):
        if not message.text:
            continue
        results.append({
            "id": message.id,
            "text": message.text,
            "chat_id": message.chat_id if message.chat else None,
            "chat_title": message.chat.title if message.chat else "Личный чат",
            "date": message.date.isoformat(),
        })
    return results

async def start_client():
    """Запускает клиент Telethon (авторизация при первом запуске)."""
    await client.start(phone=PHONE_NUMBER)
    print("Telethon client started")

async def stop_client():
    await client.disconnect()
```

**Проверка**: Этот модуль требует авторизации, поэтому тестировать будем через `main.py` позже.

**Частая ошибка**: Забывают про `SESSION` — Telethon создаёт файл сессии при первом входе, сохраняет его в папке, указанной в `TelegramClient("путь/к/сессии", ...)`. Если путь меняется или удаляется — просит код заново.

---

### 3.4 Модуль фильтрации (filter.py)

**Что делаем**: Проверяет, содержит ли сообщение хотя бы одно ключевое слово и хотя бы один город.

```python
import re
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
```

**Проверка**:
```python
# Запустить: python -c "from src.filter import is_lead; print(is_lead('Ищу свадебного фотографа в Москве'))"
# Должен вернуть True
```

**Частая ошибка**: Регистр — наш код приводит всё к lower(), поэтому регистр не важен. Если забудете lower() — не найдёт «Москва» в «москва».

---

### 3.5 Модуль БД (database.py)

**Что делаем**: Сохраняем в SQLite ID найденных сообщений, чтобы не отправлять один и тот же лид дважды.

```python
from sqlalchemy import create_engine, Column, Integer, String, BigInteger
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///data/bot.db"
engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(BigInteger, unique=True, nullable=False)
    chat_id = Column(BigInteger, nullable=False)

Base.metadata.create_all(engine)

def is_duplicate(message_id: int, chat_id: int) -> bool:
    session = SessionLocal()
    exists = session.query(Message).filter_by(
        message_id=message_id, chat_id=chat_id
    ).first() is not None
    session.close()
    return exists

def save_message(message_id: int, chat_id: int):
    session = SessionLocal()
    session.add(Message(message_id=message_id, chat_id=chat_id))
    session.commit()
    session.close()
```

**Проверка**: `python -c "from src.database import is_duplicate, save_message; save_message(123, 456); print(is_duplicate(123, 456))"` — должно вывести `True`.

**Частая ошибка**: SQLAlchemy 2.0 требует `declarative_base()` — в старых туториалах может быть `declarative_base` из другого модуля.

---

### 3.6 Модуль уведомлений (notifier.py)

**Что делаем**: Через aiogram отправляет фотографу сообщение, когда найден новый лид.

```python
from aiogram import Bot
from src.config import BOT_TOKEN, PHOTOGRAPHER_CHAT_ID

bot = Bot(token=BOT_TOKEN)

async def send_lead(lead_text: str, chat_title: str, date: str):
    message = (
        f"🔔 Найден потенциальный лид!\n\n"
        f"📌 Источник: {chat_title}\n"
        f"🕐 Дата: {date}\n"
        f"---\n{lead_text}\n---"
    )
    await bot.send_message(PHOTOGRAPHER_CHAT_ID, message)
```

**Проверка**: Можно протестировать вручную:
```python
# python -c "import asyncio; from src.notifier import send_lead; asyncio.run(send_lead('Тестовое сообщение', 'Тестовый канал', '2024-01-01'))"
```

**Частая ошибка**: Не импортировали `asyncio.run()` — aiogram-функции асинхронные, их нужно запускать через `await` или `asyncio.run()`.

---

### 3.7 main.py — точка входа

**Что делаем**: Объединяем всё вместе: запускаем Telethon, ищем по всем ключевым словам, фильтруем, проверяем дубликаты, отправляем фотографу.

```python
import asyncio
import logging
from src.config import KEYWORDS, SEARCH_INTERVAL
from src.search import client, search_messages, start_client, stop_client
from src.filter import is_lead
from src.database import is_duplicate, save_message
from src.notifier import send_lead

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_keyword(keyword: str):
    """Ищет сообщения по одному ключевому слову."""
    messages = await search_messages(keyword, limit=10)
    for msg in messages:
        text = msg["text"]
        if not is_lead(text):
            continue
        if is_duplicate(msg["id"], msg["chat_id"]):
            continue
        logger.info(f"Новый лид! {msg['chat_title']}: {text[:100]}")
        await send_lead(text, msg["chat_title"], msg["date"])
        save_message(msg["id"], msg["chat_id"])
        await asyncio.sleep(2)  # пауза между отправками, чтобы не флудить

async def main_loop():
    await start_client()
    logger.info("Бот запущен и начинает поиск...")
    try:
        while True:
            for kw in KEYWORDS:
                logger.info(f"Ищем: {kw}")
                await process_keyword(kw)
                await asyncio.sleep(5)  # пауза между ключевыми словами
            logger.info(f"Цикл завершён. Следующий через {SEARCH_INTERVAL}с")
            await asyncio.sleep(SEARCH_INTERVAL)
    finally:
        await stop_client()

if __name__ == "__main__":
    asyncio.run(main_loop())
```

**Проверка**: Запустите `python src/main.py` и убедитесь, что:
1. При первом запуске Telethon попросит ввести номер телефона и код из Telegram
2. Бот начинает искать сообщения и выводит логи
3. Если найдёт лид — приходит сообщение в Telegram фотографу

**Частая ошибка**: Telethon при первом запуске запрашивает двухфакторный пароль (2FA), если он включён на аккаунте. Код обрабатывает это через `SessionPasswordNeededError` — нужно дописать обработку, если пароль есть.

---

### 3.8 Обработка 2FA в search.py (если включена двухфакторка)

**Что делаем**: Добавляем поддержку 2FA, если на аккаунте включён дополнительный пароль.

В `src/config.py` добавьте:
```python
# Если есть 2FA пароль
TFA_PASSWORD = os.getenv("TFA_PASSWORD", "")
```

В `.env` добавьте:
```env
TFA_PASSWORD=ваш_секретный_пароль_2fa
```

В `src/search.py` измените `start_client`:

```python
async def start_client():
    await client.start(phone=PHONE_NUMBER)
    # Если хотите явно обработать 2FA:
    # await client.start(phone=PHONE_NUMBER, password=TFA_PASSWORD)
    print("Telethon client started")
```

---

## Этап 4. Docker-упаковка

### 4.1 Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "src/main.py"]
```

**Проверка**: Файл создан, лежит в корне photobot.

**Частая ошибка**: Забывают `--no-cache-dir` — образ будет больше на 100-200 МБ из-за кэша pip.

---

### 4.2 docker-compose.yml

```yaml
version: "3.9"

services:
  bot:
    build: .
    container_name: photobot
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./data:/app/data
```

**Проверка**: `docker compose config` — должен показать конфигурацию без ошибок.

**Частая ошибка**: Не указывают `restart: unless-stopped` — после перезагрузки сервера бот не запустится автоматически.

---

### 4.3 .gitignore

```gitignore
venv/
__pycache__/
*.pyc
.env
data/
```

**Проверка**: Файлы `.env` и `data/` не должны попасть в git (там пароли и сессия Telethon).

**Частая ошибка**: Забывают добавить `.env` в `.gitignore` — пароли утекают на GitHub.

---

### 4.4 Локальная сборка и тест контейнера

```bash
# Выполняется на вашем локальном компьютере, в папке photobot
docker compose build
docker compose run --rm bot   # Для первого запуска — чтобы авторизовать Telethon
```

При первом запуске Telethon запросит код из Telegram. Введите его прямо в терминал.

После успешной авторизации:
```bash
docker compose up -d   # Запуск в фоне
docker compose logs -f # Смотреть логи
```

**Проверка**: `docker compose ps` — статус `Up`. В логах — сообщения о поиске.

**Частая ошибка**: `docker compose run --rm bot` создаёт временный контейнер, но сессия Telethon сохраняется в volume (папка `data/` на вашем компьютере). Если volume не подключён — сессия не сохранится.

---

## Этап 5. Загрузка кода на VPS

### 5.1 Вариант A — через git (рекомендуется)

1. Создайте приватный репозиторий на GitHub/GitLab
2. Запушьте код:
```bash
# Локально
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/ваш-username/photobot.git
git push -u origin main
```

3. На VPS склонируйте:
```bash
ssh fotobot@<IP>
git clone https://github.com/ваш-username/photobot.git /opt/photobot
cd /opt/photobot
```

4. Создайте `.env` на сервере (заполните теми же данными, что в локальном):
```bash
nano /opt/photobot/.env
# Вставьте содержимое .env с вашего компьютера
```

5. Создайте папку для данных:
```bash
mkdir -p /opt/photobot/data
```

**Частая ошибка**: Используют публичный репозиторий — все увидят ваш Bot Token и api_hash. Только приватный репозиторий!

---

### 5.2 Вариант B — через scp (без git, для новичков)

```bash
# Локально — копируем папку проекта на VPS
scp -r /путь/к/photobot fotobot@<IP>:/opt/photobot
```

Потом на VPS:
```bash
ssh fotobot@<IP>
cd /opt/photobot
# Создайте .env на сервере
nano .env
# Вставьте содержимое .env
mkdir -p data
```

**Проверка**: `ls /opt/photobot` показывает все файлы проекта.

**Частая ошибка**: scp копирует и `venv/` (если не добавили в .gitignore) — это лишние гигабайты, которые не нужны на сервере.

---

## Этап 6. Запуск на VPS

### 6.1 Сборка и запуск

```bash
# Выполняется на VPS
cd /opt/photobot
docker compose up -d --build
```

**Флаги**:
- `-d` — detach, работает в фоне
- `--build` — пересобрать образ перед запуском (нужно при первом запуске и после обновления кода)

**Проверка**: `docker compose ps` — контейнер `photobot` в статусе `Up`.

---

### 6.2 Первая авторизация Telethon на сервере

**Что делаем**: При первом запуске Telethon попросит ввести код из Telegram. Для этого нужно запустить контейнер в интерактивном режиме.

```bash
# Выполняется на VPS
cd /opt/photobot
docker compose run --rm bot
```

Вы увидите: `Please enter your phone: +71234567890` — нажмите Enter (номер уже в .env). Потом придёт код в Telegram технического аккаунта — введите его в терминал.

**Проверка**: В логах появится `Telethon client started` — значит, авторизация прошла успешно.

**Важно**: После этого нажмите Ctrl+C, чтобы остановить временный контейнер, и запустите обычный:
```bash
docker compose up -d
```

**Частая ошибка**: Пытаются ввести код через `docker compose logs` — это не интерактивный режим. Используйте `docker compose run --rm bot`.

---

### 6.3 Проверка автозапуска

**Что делаем**: Убеждаемся, что `restart: unless-stopped` работает (мы уже указали это в docker-compose.yml).

```bash
sudo reboot now   # Перезагружаем сервер
```
Подождите 1-2 минуты, зайдите снова:
```bash
ssh fotobot@<IP>
docker compose ps   # Должен быть Up
```

**Проверка**: Статус `Up` (без ручного запуска).

**Частая ошибка**: Не ждут 1-2 минуты после перезагрузки — Docker может стартовать не сразу.

---

## Этап 7. Проверка и мониторинг

### 7.1 Просмотр логов

```bash
# На VPS
docker compose logs -f   # Следить за логами в реальном времени
docker compose logs --tail=50   # Последние 50 строк
```

**Что смотреть**: Ищет ли бот сообщения (`Ищем: свадьба`), находит ли лиды (`Новый лид!`), нет ли ошибок.

**Частая ошибка**: Забывают флаг `-f` — тогда логи показываются и терминал закрывается. С `-f` они обновляются в реальном времени. Нажмите Ctrl+C, чтобы выйти.

---

### 7.2 Проверка отправки уведомлений

**Что делаем**: Отправляем тестовое сообщение в Telegram фотографу, чтобы убедиться, что бот работает.

Самый простой способ — написать боту в Telegram любое сообщение. Если бот отвечает (даже если просто игнорирует), значит он работает.

Можно также проверить в логах:
```bash
docker compose logs --tail=20
```
Там должно быть `Telethon client started` и периодические `Ищем: ...`.

**Проверка**: Фотограф получает сообщение в Telegram, когда бот находит подходящий лид.

---

### 7.3 Использование ресурсов

```bash
docker stats   # Показывает CPU, память, сеть для всех контейнеров
```

**Проверка**: Нормальное потребление — 50-200 MB RAM, CPU < 1% в простое.

**Частая ошибка**: `docker stats` показывает непрерывно, нажмите Ctrl+C для выхода.

---

## Этап 8. Обслуживание

### 8.1 Обновление кода и пересборка

Когда вносите изменения в код локально:

```bash
# Локально
git add .
git commit -m "Описание изменений"
git push

# На VPS
cd /opt/photobot
git pull
docker compose up -d --build
```

**Проверка**: `docker compose logs --tail=5` — покажет новую версию бота.

**Частая ошибка**: Забывают сделать `git pull` перед `docker compose up -d --build` — собирается старая версия.

---

### 8.2 Бэкап данных

**Что делаем**: Копируем папку с БД и сессией Telethon в надёжное место.

```bash
# На VPS — создаём архив
tar -czf photobot_backup_$(date +%Y%m%d).tar.gz /opt/photobot/data

# Скачиваем на локальный компьютер
scp fotobot@<IP>:~/photobot_backup_*.tar.gz ./
```

**Проверка**: Файл архива создан и не пустой (`ls -lh *.tar.gz`).

**Частая ошибка**: Не делают бэкап перед обновлением — если что-то пойдёт не так, сессию Telethon придётся авторизовывать заново.

---

### 8.3 Остановка и перезапуск

```bash
# Остановить
docker compose down

# Запустить снова
docker compose up -d

# Перезапустить
docker compose restart
```

**Проверка**: После `restart` статус `Up`, в логах нет ошибок.

---

### 8.4 Ротация логов Docker

По умолчанию Docker-логи могут бесконечно расти. Настроим ограничение.

Создайте или отредактируйте `/etc/docker/daemon.json` на VPS:

```bash
sudo nano /etc/docker/daemon.json
```

Вставьте:
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

Перезапустите Docker:
```bash
sudo systemctl restart docker
cd /opt/photobot
docker compose up -d
```

**Проверка**: Логи не будут занимать больше 30 МБ (3 файла по 10 МБ).

**Частая ошибка**: После перезапуска Docker контейнер нужно запустить заново (`docker compose up -d`).

---

## Приложение: Часто задаваемые вопросы

### Где найти Chat ID фотографа?
Напишите @userinfobot в Telegram — он покажет ваш ID (и ID любого пересланного сообщения).

### Бот не видит сообщения в закрытых каналах?
Telethon (user-аккаунт) может читать только те каналы/группы, в которые добавлен аккаунт. Если аккаунт не подписан на канал — сообщения оттуда не попадут в поиск. Добавьте технический аккаунт в нужные каналы.

### Telethon запрашивает код каждый раз при запуске?
Нет, если есть файл сессии (`data/telethon_session.session`). Если файл удаляется или пересоздаётся папка — да, придётся вводить код заново. Volume в docker-compose гарантирует, что файл сохраняется между перезапусками.

### Что делать, если аккаунт заблокировали?
1. Попробуйте через web.telegram.org — если и там не заходит, аккаунт заблокирован
2. Используйте запасной номер (поэтому мы и рекомендовали отдельный номер)
3. Напишите в поддержку Telegram (@ TelegramSupport) — иногда разблокируют

### aiogram и Telethon не конфликтуют?
Нет. aiogram работает как бот (через Bot API), Telethon — как user-аккаунт (через MTProto). Они не пересекаются. В docker-compose у нас один контейнер, внутри которого работают обе библиотеки параллельно.

---

## Чек-лист: готовность к запуску

- [ ] VPS: SSH работает под пользователем `fotobot`
- [ ] VPS: UFW включён, SSH разрешён
- [ ] VPS: Docker установлен, `docker ps` работает без sudo
- [ ] Получены: Bot Token, api_id, api_hash
- [ ] Создан отдельный технический аккаунт Telegram
- [ ] Локально: `venv` активирован, зависимости установлены
- [ ] Локально: бот запускается, Telethon авторизован, приходят тестовые лиды
- [ ] Docker-образ собирается локально
- [ ] Код загружен на VPS
- [ ] На VPS: `docker compose up -d --build` выполнен без ошибок
- [ ] На VPS: Telethon авторизован (код введён)
- [ ] В Telegram фотографа приходят уведомления о лидах
