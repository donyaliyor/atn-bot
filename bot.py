"""
Attendance Bot - Main Entry Point
A Telegram bot for teacher attendance tracking with location validation.

This bot enables teachers to check in and out using location verification,
supports multiple languages (EN/RU/UZ), and provides admin features.
"""
import logging
import sys
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

from config import Config
from database.models import Teacher
from locales import get_message

# Configure logging with professional format
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, Config.LOG_LEVEL),
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/bot.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /start command.
    Sends a welcome message to the user and registers them in database.

    Args:
        update: Telegram update object
        context: Callback context
    """
    user = update.effective_user
    logger.info(f"User {user.id} ({user.username}) started the bot")

    # Register/update user in database
    success = Teacher.create_or_update(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language=Config.DEFAULT_LANGUAGE
    )

    if success:
        logger.info(f"User {user.id} registered/updated in database")
    else:
        logger.error(f"Failed to register user {user.id} in database")

    # Get user's language (will be default for new users)
    lang = Teacher.get_language(user.id)

    # Send welcome message
    message = get_message(
        lang,
        'welcome',
        first_name=user.first_name,
        radius=Config.RADIUS_METERS,
        user_id=user.id,
        full_name=f"{user.first_name} {user.last_name or ''}".strip()
    )

    await update.message.reply_text(message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /help command.
    Shows available commands and usage information.

    Args:
        update: Telegram update object
        context: Callback context
    """
    user = update.effective_user
    logger.info(f"User {user.id} requested help")

    lang = Teacher.get_language(user.id)
    is_admin = Config.is_admin(user.id)

    message = get_message(lang, 'help_user')

    if is_admin:
        message += get_message(lang, 'help_admin')

    await update.message.reply_text(message, parse_mode='Markdown')


async def myid_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /myid command.
    Shows user their Telegram ID and admin status.

    Args:
        update: Telegram update object
        context: Callback context
    """
    user = update.effective_user
    lang = Teacher.get_language(user.id)
    is_admin = Config.is_admin(user.id)

    message = get_message(
        lang,
        'myid',
        user_id=user.id,
        username=user.username or get_message(lang, 'na'),
        full_name=f"{user.first_name} {user.last_name or ''}".strip(),
        language=lang.upper(),
        admin_status=get_message(lang, 'yes') if is_admin else get_message(lang, 'no')
    )

    logger.info(f"User {user.id} requested their ID")
    await update.message.reply_text(message, parse_mode='Markdown')


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /status command.
    Shows user's attendance status for today.

    Args:
        update: Telegram update object
        context: Callback context
    """
    user = update.effective_user
    logger.info(f"User {user.id} requested status")

    from database.models import Attendance
    from datetime import datetime

    lang = Teacher.get_language(user.id)
    status = Attendance.get_today_status(user.id)

    if not status:
        message = get_message(lang, 'status_not_checked_in')
    else:
        check_in_time = datetime.fromisoformat(status['check_in_time'])

        if status['check_out_time']:
            check_out_time = datetime.fromisoformat(status['check_out_time'])
            message = get_message(
                lang,
                'status_complete',
                checkin_time=check_in_time.strftime('%H:%M:%S'),
                checkout_time=check_out_time.strftime('%H:%M:%S'),
                hours=f"{status['total_hours']:.2f}"
            )
        else:
            message = get_message(
                lang,
                'status_checked_in',
                checkin_time=check_in_time.strftime('%H:%M:%S')
            )

    await update.message.reply_text(message, parse_mode='Markdown')


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /history command.
    Shows user's recent attendance history.

    Args:
        update: Telegram update object
        context: Callback context
    """
    user = update.effective_user
    logger.info(f"User {user.id} requested history")

    from database.models import Attendance
    from datetime import datetime

    lang = Teacher.get_language(user.id)
    history = Attendance.get_user_history(user.id, limit=7)

    if not history:
        message = get_message(lang, 'history_empty')
    else:
        message = get_message(lang, 'history_header')

        for record in history:
            date_str = record['date']
            check_in = datetime.fromisoformat(record['check_in_time']).strftime('%H:%M')

            if record['check_out_time']:
                check_out = datetime.fromisoformat(record['check_out_time']).strftime('%H:%M')
                hours = record['total_hours']
                message += f"📅 {date_str}\n  ✅ {check_in} → 🚪 {check_out} ({hours:.1f}h)\n\n"
            else:
                message += f"📅 {date_str}\n  ✅ {check_in} → ⏳ Not checked out\n\n"

    await update.message.reply_text(message, parse_mode='Markdown')


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /stats command.
    Shows database statistics (admin only).

    Args:
        update: Telegram update object
        context: Callback context
    """
    user = update.effective_user

    if not Config.is_admin(user.id):
        lang = Teacher.get_language(user.id)
        message = get_message(lang, 'error_admin_only')
        await update.message.reply_text(message, parse_mode='Markdown')
        return

    logger.info(f"Admin {user.id} requested stats")

    from database.db import get_db_stats

    stats = get_db_stats()
    active_teachers = len(Teacher.get_all_active())

    message = (
        f"📊 **Database Statistics**\n\n"
        f"👥 Total Teachers: {stats['teachers']}\n"
        f"✅ Active Teachers: {active_teachers}\n"
        f"📝 Attendance Records: {stats['attendance_records']}\n"
        f"📋 Admin Logs: {stats['admin_logs']}\n\n"
        f"🔧 Database: {Config.DB_PATH}\n"
        f"📍 School Location: ({Config.SCHOOL_LATITUDE:.4f}, {Config.SCHOOL_LONGITUDE:.4f})\n"
        f"📏 Check-in Radius: {Config.RADIUS_METERS}m"
    )

    await update.message.reply_text(message, parse_mode='Markdown')


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle errors in the bot.
    Logs errors and notifies the user if possible.

    Args:
        update: Update object (can be None)
        context: Callback context with error information
    """
    logger.error(f"Exception while handling an update: {context.error}", exc_info=context.error)

    # Try to notify the user
    if isinstance(update, Update) and update.effective_message:
        try:
            lang = Teacher.get_language(update.effective_user.id) if update.effective_user else 'en'
            message = get_message(lang, 'error_general')
            await update.effective_message.reply_text(message)
        except Exception as e:
            logger.error(f"Failed to send error message to user: {e}")


def main() -> None:
    """
    Start the bot.
    Main entry point for the application.
    """
    logger.info("=" * 60)
    logger.info("Starting Attendance Bot...")
    logger.info("=" * 60)

    # Validate configuration
    logger.info("Validating configuration...")
    if not Config.validate():
        logger.error("Configuration validation failed. Exiting.")
        sys.exit(1)

    # Initialize database
    logger.info("Initializing database...")
    try:
        from database.db import init_database, get_db_stats
        init_database()
        stats = get_db_stats()
        logger.info(f"Database initialized successfully:")
        logger.info(f"  - Teachers: {stats['teachers']}")
        logger.info(f"  - Attendance Records: {stats['attendance_records']}")
        logger.info(f"  - Admin Logs: {stats['admin_logs']}")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        logger.error("Please check database permissions and configuration")
        sys.exit(1)

    # Log configuration details
    logger.info("=" * 60)
    logger.info("Configuration:")
    logger.info(f"  - School Location: ({Config.SCHOOL_LATITUDE:.6f}, {Config.SCHOOL_LONGITUDE:.6f})")
    logger.info(f"  - Check-in Radius: {Config.RADIUS_METERS}m")
    logger.info(f"  - Admin Users: {len(Config.ADMIN_USER_IDS)}")
    logger.info(f"  - Supported Languages: {', '.join(Config.SUPPORTED_LANGUAGES)}")
    logger.info(f"  - Default Language: {Config.DEFAULT_LANGUAGE}")
    logger.info(f"  - Timezone: {Config.TIMEZONE}")
    logger.info(f"  - Log Level: {Config.LOG_LEVEL}")
    logger.info("=" * 60)

    # Create application
    logger.info("Building Telegram application...")
    application = Application.builder().token(Config.BOT_TOKEN).build()

    # Register basic command handlers
    logger.info("Registering command handlers...")
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("myid", myid_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("stats", stats_command))

    # Register language handlers
    from handlers.start import language_command, language_callback
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))

    # Register attendance handlers
    from handlers.attendance import (
        checkin_command,
        checkout_command,
        handle_location,
        cancel_command
    )
    application.add_handler(CommandHandler("checkin", checkin_command))
    application.add_handler(CommandHandler("checkout", checkout_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))

    # Register error handler
    application.add_error_handler(error_handler)

    logger.info("All handlers registered successfully")
    logger.info("=" * 60)

    # Start the bot
    logger.info("🚀 Bot is ready! Starting polling...")
    logger.info("=" * 60)
    logger.info("Supported Languages: EN, RU, UZ")
    logger.info("Press Ctrl+C to stop the bot")
    logger.info("=" * 60)

    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        logger.info("=" * 60)
        logger.info("Bot stopped by user (Ctrl+C)")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.error("Bot stopped due to error")
        sys.exit(1)


if __name__ == '__main__':
    main()
