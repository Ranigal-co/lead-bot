# PhotoBot — Telegram Lead Finder for Photographers

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED)](https://docker.com)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-blueviolet)](https://docs.aiogram.dev)
[![Telethon](https://img.shields.io/badge/Telethon-1.x-26A5E4)](https://docs.telethon.dev)

A Telegram bot that monitors Telegram global search for photographer-related keywords, filters results by city, and forwards matching leads to the photographer via Telegram notifications.

## Features

- **Keyword & City Filtering** — searches Telegram global search and filters messages containing specified keywords and city names
- **Deduplication** — stores processed messages in SQLite to avoid duplicate notifications
- **Dual Operation Modes**:
  - **Live Mode** — uses Telethon (user account) to perform real Telegram global search
  - **Mock Mode** — generates test leads for development and demo purposes (auto-enabled when Telethon credentials are not configured)
- **Docker Support** — ready for containerized deployment on any VPS

## Tech Stack

- **Bot API**: aiogram 3.x
- **Telegram Client**: Telethon 1.x (MTProto)
- **Database**: SQLAlchemy + SQLite
- **Configuration**: python-dotenv
- **Containerization**: Docker + docker-compose

## Quick Start

### Prerequisites

- Python 3.12+
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Telegram API credentials (from [my.telegram.org](https://my.telegram.org)) — optional, required only for live search

### Local Development

```bash
# Clone the repository
git clone https://github.com/your-username/photobot.git
cd photobot

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\Activate.ps1 on Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your bot token and preferences

# Run (mock mode — no Telethon credentials needed)
python -m src.main
```

### Docker

```bash
docker compose up --build
```

The bot will start in mock mode and send test leads to the configured Telegram chat.

## Project Structure

```
├── src/
│   ├── config.py      # Environment configuration
│   ├── search.py      # Telegram search (Telethon + mock fallback)
│   ├── filter.py      # Keyword and city filtering logic
│   ├── database.py    # SQLite deduplication storage
│   ├── notifier.py    # Lead notification via aiogram
│   └── main.py        # Application entry point
├── data/              # Runtime data (DB, session files)
├── .env.example       # Environment template
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Security

- Sensitive data (tokens, API keys) are loaded from `.env` — never committed to the repository
- `.env.example` serves as a template with placeholder values
- The Telegram user account used for search should be a dedicated account (not personal) to comply with Telegram ToS

## License

MIT
