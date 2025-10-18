# Attendance Bot 🏫

A professional Telegram bot for tracking teacher attendance with location-based verification.

## Features

- 📍 Location-based check-in/check-out (50m radius validation)
- 🌍 Multi-language support (English, Russian, Uzbek)
- 👥 Admin panel for monitoring
- 📊 CSV export functionality
- 📅 Weekday-only operation
- 🔒 Secure and privacy-focused

## Current Status: Step 1 ✅

**Working Features:**
- ✅ Bot responds to `/start` and `/help` commands
- ✅ Professional logging system
- ✅ Configuration management
- ✅ Error handling

**Next Steps:**
- ⏳ Database integration
- ⏳ Location validation
- ⏳ Check-in/check-out functionality
- ⏳ Multi-language support
- ⏳ Admin panel

## Setup

### Prerequisites

- Python 3.11 or higher
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)

### Installation

1. **Create and activate virtual environment:**
```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
   pip install -r requirements.txt
```

3. **Configure environment:**
```bash
   cp .env.example .env
   # Edit .env with your bot token and settings
```

4. **Get your bot token:**
   - Talk to [@BotFather](https://t.me/BotFather) on Telegram
   - Send `/newbot` and follow instructions
   - Copy the token and add it to `.env`

5. **Run the bot:**
```bash
   python bot.py
```

## Configuration

Edit `.env` file:
```bash
# Required
BOT_TOKEN=your_bot_token_here

# School location (get from Google Maps)
SCHOOL_LATITUDE=41.2995
SCHOOL_LONGITUDE=69.2401
RADIUS_METERS=50

# Admin user IDs (get your ID from @userinfobot)
ADMIN_USER_IDS=123456789,987654321
```

## Usage

### For Teachers:
- `/start` - Initialize bot
- `/help` - Show help message

### For Admins:
- Same as teachers for now
- Admin panel coming in Step 6

## Project Structure
```
attendance-bot/
├── bot.py              # Main entry point
├── config.py           # Configuration management
├── handlers/           # Command handlers (empty for now)
├── database/           # Database operations (empty for now)
├── utils/              # Utility functions (empty for now)
├── locales/            # Translations (empty for now)
├── logs/               # Log files
└── requirements.txt    # Python dependencies
```

## Development

### Running in Development Mode
```bash
# Set LOG_LEVEL=DEBUG in .env for verbose logging
python bot.py
```

### Testing the Bot

1. Start the bot
2. Open Telegram
3. Search for your bot by username
4. Send `/start` command
5. You should receive a welcome message!

## Troubleshooting

### Bot doesn't respond
- Check if bot is running in terminal
- Verify `BOT_TOKEN` in `.env` is correct
- Check logs in `logs/bot.log`

### Configuration errors
- Run `python -c "from config import Config; Config.validate()"`
- Check all required env vars are set

## License

MIT License - Build something awesome!

## Credits

Built with [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) v20.7
