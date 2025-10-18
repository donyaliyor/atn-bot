# Attendance Bot

A Telegram bot for tracking teacher attendance with location-based verification.

## Features

- Location-based check-in/check-out with 50m radius validation
- Multi-language support (English, Russian, Uzbek)
- Persistent menu buttons for quick access
- Admin panel with attendance reports and CSV export
- Zero-downtime deployment on Fly.io
- Weekday-only operation with automatic validation

## Requirements

- Python 3.11+
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- Fly.io account (for deployment)

## Local Setup
```bash
# Clone and setup
git clone <repository-url>
cd attendance-bot
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your settings

# Run
python bot.py
```

## Configuration

Required environment variables in `.env`:
```bash
BOT_TOKEN=your_bot_token_here
SCHOOL_LATITUDE=41.2995
SCHOOL_LONGITUDE=69.2401
RADIUS_METERS=50
ADMIN_USER_IDS=123456789,987654321
TIMEZONE=Asia/Tashkent
```

## Deployment
```bash
# Install Fly.io CLI
curl -L https://fly.io/install.sh | sh

# Deploy
flyctl launch --no-deploy
flyctl volumes create attendance_data --region ams --size 1
flyctl secrets set BOT_TOKEN=your_token ADMIN_USER_IDS=your_id
flyctl deploy

# Set bot commands (one-time)
flyctl ssh console
python commands.py
exit
```

## Commands

**User Commands:**
- `/start` - Register and show menu
- `/checkin` - Check in with location
- `/checkout` - Check out with location
- `/status` - View today's attendance
- `/history` - View last 7 days
- `/language` - Change language
- `/help` - Show help

**Admin Commands:**
- `/admin` - Access admin panel
- `/stats` - View database statistics

## Project Structure
```
attendance-bot/
├── bot.py              # Main entry point
├── commands.py         # Bot commands setup
├── config.py           # Configuration
├── handlers/           # Command handlers
│   ├── start.py        # Start & language
│   ├── attendance.py   # Check-in/out
│   └── admin.py        # Admin panel
├── database/           # Database layer
│   ├── db.py           # Connection management
│   └── models.py       # Data models
├── utils/              # Utilities
│   ├── keyboards.py    # Button layouts
│   ├── location.py     # Location validation
│   └── decorators.py   # Handler decorators
├── locales/            # Translations
│   ├── en.py
│   ├── ru.py
│   └── uz.py
└── fly.toml            # Deployment config
```

## Development
```bash
# Run locally
python bot.py

# Set commands
python commands.py

# View logs
flyctl logs  # Production
tail -f logs/bot.log  # Local
```

## Architecture

- **Database:** SQLite with context managers
- **Location:** Geopy geodesic distance calculation
- **Deployment:** Fly.io with blue-green strategy
- **Health Check:** HTTP server on port 8080
- **Zero Downtime:** 2 instances with health checks

## License

MIT License

## Built With

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) v20.7
- [geopy](https://github.com/geopy/geopy) v2.4.1
