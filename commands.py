"""
Set bot commands menu in Telegram.
This script configures the command menu that appears when users type '/' in the chat.

Run once after deployment:
    python commands.py

Or set up commands for specific language:
    python commands.py --lang en
    python commands.py --lang ru
    python commands.py --lang uz
"""
import asyncio
import sys
from telegram import Bot, BotCommand, BotCommandScopeDefault, BotCommandScopeAllPrivateChats
from config import Config

# Command definitions for each language
COMMANDS = {
    'en': [
        BotCommand("start", "Start the bot and register"),
        BotCommand("checkin", "Check in with location"),
        BotCommand("checkout", "Check out with location"),
        BotCommand("status", "View today's attendance status"),
        BotCommand("history", "View attendance history (last 7 days)"),
        BotCommand("language", "Change language (EN/RU/UZ)"),
        BotCommand("notifications", "Toggle notification reminders"),
        BotCommand("myid", "Show your user ID and info"),
        BotCommand("help", "Show help and available commands"),
        BotCommand("cancel", "Cancel current operation"),
        BotCommand("admin", "Admin panel (admins only)"),
        BotCommand("schedule", "View work schedule (admins only)"),
        BotCommand("stats", "View statistics (admins only)"),
    ],
    'ru': [
        BotCommand("start", "Запустить бота и зарегистрироваться"),
        BotCommand("checkin", "Отметиться (приход)"),
        BotCommand("checkout", "Отметиться (уход)"),
        BotCommand("status", "Посмотреть сегодняшний статус"),
        BotCommand("history", "История посещений (последние 7 дней)"),
        BotCommand("language", "Изменить язык (EN/RU/UZ)"),
        BotCommand("notifications", "Переключить уведомления"),
        BotCommand("myid", "Показать ваш ID и информацию"),
        BotCommand("help", "Показать справку и команды"),
        BotCommand("cancel", "Отменить текущую операцию"),
        BotCommand("admin", "Панель администратора (только админы)"),
        BotCommand("schedule", "Просмотр расписания (только админы)"),
        BotCommand("stats", "Статистика (только админы)"),
    ],
    'uz': [
        BotCommand("start", "Botni ishga tushirish va ro'yxatdan o'tish"),
        BotCommand("checkin", "Kelish vaqtini belgilash"),
        BotCommand("checkout", "Ketish vaqtini belgilash"),
        BotCommand("status", "Bugungi holatni ko'rish"),
        BotCommand("history", "Davomat tarixi (oxirgi 7 kun)"),
        BotCommand("language", "Tilni o'zgartirish (EN/RU/UZ)"),
        BotCommand("notifications", "Bildirishnomalarni yoqish/o'chirish"),
        BotCommand("myid", "ID va ma'lumotlarni ko'rsatish"),
        BotCommand("help", "Yordam va buyruqlarni ko'rsatish"),
        BotCommand("cancel", "Joriy operatsiyani bekor qilish"),
        BotCommand("admin", "Administrator paneli (faqat adminlar)"),
        BotCommand("schedule", "Ish jadvali (faqat adminlar)"),
        BotCommand("stats", "Statistika (faqat adminlar)"),
    ]
}


async def set_commands_for_language(bot: Bot, lang: str) -> None:
    """
    Set bot commands for a specific language.

    Args:
        bot: Telegram Bot instance
        lang: Language code ('en', 'ru', 'uz')
    """
    if lang not in COMMANDS:
        print(f"❌ Error: Language '{lang}' not supported. Use: en, ru, uz")
        return

    try:
        await bot.set_my_commands(
            commands=COMMANDS[lang],
            language_code=lang
        )
        print(f"✅ Commands set for language: {lang.upper()}")
    except Exception as e:
        print(f"❌ Error setting commands for {lang}: {e}")


async def set_all_commands(bot: Bot) -> None:
    """
    Set bot commands for all supported languages.

    Args:
        bot: Telegram Bot instance
    """
    print("🚀 Setting bot commands for all languages...\n")

    # Set default commands (English)
    try:
        await bot.set_my_commands(
            commands=COMMANDS['en'],
            scope=BotCommandScopeDefault()
        )
        print("✅ Default commands set (English)")
    except Exception as e:
        print(f"❌ Error setting default commands: {e}")

    # Set commands for each language
    for lang in ['en', 'ru', 'uz']:
        await set_commands_for_language(bot, lang)

    print("\n" + "="*60)
    print("✨ All commands configured successfully!")
    print("="*60)
    print("\n📱 Users will now see commands in their language")
    print("💡 Commands appear when typing '/' in the chat")
    print("🔄 Changes take effect immediately\n")


async def delete_commands(bot: Bot) -> None:
    """
    Delete all bot commands.

    Args:
        bot: Telegram Bot instance
    """
    print("🗑️  Deleting all bot commands...\n")

    try:
        # Delete default commands
        await bot.delete_my_commands(scope=BotCommandScopeDefault())
        print("✅ Default commands deleted")

        # Delete language-specific commands
        for lang in ['en', 'ru', 'uz']:
            await bot.delete_my_commands(language_code=lang)
            print(f"✅ Commands deleted for: {lang.upper()}")

        print("\n✨ All commands deleted successfully!\n")
    except Exception as e:
        print(f"❌ Error deleting commands: {e}")


async def show_current_commands(bot: Bot) -> None:
    """
    Show currently configured commands.

    Args:
        bot: Telegram Bot instance
    """
    print("📋 Current bot commands:\n")

    try:
        # Get default commands
        commands = await bot.get_my_commands(scope=BotCommandScopeDefault())

        if commands:
            print("Default commands (English):")
            for cmd in commands:
                print(f"  /{cmd.command} - {cmd.description}")
            print()
        else:
            print("No default commands set.\n")

        # Get language-specific commands
        for lang in ['en', 'ru', 'uz']:
            commands = await bot.get_my_commands(language_code=lang)
            if commands:
                print(f"{lang.upper()} commands:")
                for cmd in commands:
                    print(f"  /{cmd.command} - {cmd.description}")
                print()
    except Exception as e:
        print(f"❌ Error getting commands: {e}")


def print_usage():
    """Print usage information."""
    print("\n" + "="*60)
    print("📚 Bot Commands Configuration Tool")
    print("="*60)
    print("\nUsage:")
    print("  python commands.py              - Set commands for all languages")
    print("  python commands.py --lang en    - Set commands for English only")
    print("  python commands.py --lang ru    - Set commands for Russian only")
    print("  python commands.py --lang uz    - Set commands for Uzbek only")
    print("  python commands.py --show       - Show current commands")
    print("  python commands.py --delete     - Delete all commands")
    print("  python commands.py --help       - Show this help message")
    print("\nExamples:")
    print("  python commands.py")
    print("  python commands.py --lang ru")
    print("  python commands.py --show")
    print("\n" + "="*60 + "\n")


async def main():
    """Main function to set bot commands."""

    # Check if bot token is configured
    if not Config.BOT_TOKEN:
        print("❌ Error: BOT_TOKEN not found in environment variables")
        print("💡 Make sure .env file exists and contains BOT_TOKEN")
        return

    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()

        if arg in ['--help', '-h', 'help']:
            print_usage()
            return
        elif arg == '--show':
            bot = Bot(Config.BOT_TOKEN)
            await show_current_commands(bot)
            return
        elif arg == '--delete':
            bot = Bot(Config.BOT_TOKEN)
            await delete_commands(bot)
            return
        elif arg == '--lang':
            if len(sys.argv) < 3:
                print("❌ Error: Please specify language (en, ru, uz)")
                print("Example: python commands.py --lang en")
                return

            lang = sys.argv[2].lower()
            if lang not in ['en', 'ru', 'uz']:
                print(f"❌ Error: Invalid language '{lang}'")
                print("Available languages: en, ru, uz")
                return

            bot = Bot(Config.BOT_TOKEN)
            await set_commands_for_language(bot, lang)
            return
        else:
            print(f"❌ Unknown argument: {arg}")
            print_usage()
            return

    # Default: Set commands for all languages
    bot = Bot(Config.BOT_TOKEN)
    await set_all_commands(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        print("💡 Check your BOT_TOKEN in .env file")
        sys.exit(1)
