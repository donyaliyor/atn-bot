"""
Attendance Bot - Main Entry Point
A Telegram bot for teacher attendance tracking with location validation.

This bot enables teachers to check in and out using location verification,
supports multiple languages (EN/RU/UZ), and provides admin features.

FIX: Enhanced error handler with robust error message delivery
"""
import logging
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
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
from utils.keyboards import get_main_menu_keyboard, remove_keyboard

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, Config.LOG_LEVEL),
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/bot.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for health checks."""

    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


def run_health_server():
    """Run health check server in background thread."""
    try:
        server = HTTPServer(('0.0.0.0', 8080), HealthCheckHandler)
        server.serve_forever()
    except Exception as e:
        logger.error(f"Health check server error: {e}")


def setup_notification_jobs(application: Application) -> None:
    """
    Set up all scheduled notification jobs using Config-based work schedule.

    COMMIT 2 FIX: Removed job_kwargs timezone parameter that was causing
    "got multiple values for keyword argument 'timezone'" error.
    The timezone is embedded in the time objects themselves.

    Args:
        application: Telegram application instance
    """
    logger.info("=" * 60)
    logger.info("SETTING UP NOTIFICATION JOBS")
    logger.info("=" * 60)

    try:
        import pytz
        from handlers.notifications import (
            send_morning_reminder,
            send_late_warning,
            send_checkout_reminder,
            send_forgotten_checkout
        )

        job_queue = application.job_queue

        try:
            tz = pytz.timezone(Config.TIMEZONE)
            logger.info(f"Using timezone: {Config.TIMEZONE}")
        except Exception as e:
            logger.error(f"Error loading timezone {Config.TIMEZONE}: {e}")
            logger.warning("Falling back to UTC")
            tz = pytz.UTC

        notification_times = Config.get_notification_times()

        logger.info("Notification times calculated from work schedule:")
        logger.info(f"  - Work Hours: {Config.WORK_START_TIME} - {Config.WORK_END_TIME}")
        logger.info(f"  - Grace Period: {Config.GRACE_PERIOD_MINUTES} minutes")
        logger.info(f"  - Work Days: {Config.WORK_DAYS}")
        logger.info("")

        morning_time = notification_times['morning_reminder']
        job_queue.run_daily(
            send_morning_reminder,
            time=morning_time,
            days=(0, 1, 2, 3, 4),
            name='morning_reminder'
        )
        logger.info(f"✅ Morning Reminder scheduled: {morning_time.strftime('%H:%M')} (weekdays)")

        late_time = notification_times['late_warning']
        job_queue.run_daily(
            send_late_warning,
            time=late_time,
            days=(0, 1, 2, 3, 4),
            name='late_warning'
        )
        logger.info(f"✅ Late Warning scheduled: {late_time.strftime('%H:%M')} (weekdays)")

        checkout_time = notification_times['checkout_reminder']
        job_queue.run_daily(
            send_checkout_reminder,
            time=checkout_time,
            days=(0, 1, 2, 3, 4),
            name='checkout_reminder'
        )
        logger.info(f"✅ Checkout Reminder scheduled: {checkout_time.strftime('%H:%M')} (weekdays)")

        forgotten_time = notification_times['forgotten_checkout']
        job_queue.run_daily(
            send_forgotten_checkout,
            time=forgotten_time,
            days=(0, 1, 2, 3, 4),
            name='forgotten_checkout'
        )
        logger.info(f"✅ Forgotten Checkout Alert scheduled: {forgotten_time.strftime('%H:%M')} (weekdays)")

        logger.info("")
        logger.info("All notification jobs scheduled successfully!")
        logger.info("=" * 60)

    except ImportError as e:
        logger.error(f"Error importing notification handlers: {e}")
        logger.error("Notification system will not be available")
    except Exception as e:
        logger.error(f"Error setting up notification jobs: {e}", exc_info=True)
        logger.error("Bot will continue without scheduled notifications")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    user = update.effective_user
    logger.info(f"User {user.id} ({user.username}) started the bot")

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

    lang = Teacher.get_language(user.id)

    message = get_message(
        lang,
        'welcome',
        first_name=user.first_name,
        radius=Config.RADIUS_METERS,
        user_id=user.id,
        full_name=f"{user.first_name} {user.last_name or ''}".strip()
    )

    await update.message.reply_text(
        message,
        parse_mode='Markdown',
        reply_markup=get_main_menu_keyboard(lang)
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    user = update.effective_user
    logger.info(f"User {user.id} requested help")

    lang = Teacher.get_language(user.id)
    is_admin = Config.is_admin(user.id)

    message = get_message(lang, 'help_user')

    if is_admin:
        message += get_message(lang, 'help_admin')

    await update.message.reply_text(message, parse_mode='Markdown')


async def myid_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /myid command."""
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
    """Handle the /status command."""
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
    """Handle the /history command."""
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
                message += f"{date_str}\n  ✅ {check_in} → {check_out} ({hours:.1f}h)\n\n"
            else:
                message += f"{date_str}\n  ✅ {check_in} → Not checked out\n\n"

    await update.message.reply_text(message, parse_mode='Markdown')


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /stats command."""
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
        f"**Database Statistics**\n\n"
        f"Total Teachers: {stats['teachers']}\n"
        f"Active Teachers: {active_teachers}\n"
        f"Attendance Records: {stats['attendance_records']}\n"
        f"Admin Logs: {stats['admin_logs']}\n\n"
        f"**Notifications (Phase 2)**\n"
        f"Total Sent: {stats.get('notifications_total', 0)}\n"
        f"This Week: {stats.get('notifications_this_week', 0)}\n"
        f"Enabled Users: {stats.get('notifications_enabled_users', 0)}\n\n"
        f"Database: {Config.DB_PATH}\n"
        f"School Location: ({Config.SCHOOL_LATITUDE:.4f}, {Config.SCHOOL_LONGITUDE:.4f})\n"
        f"Check-in Radius: {Config.RADIUS_METERS}m"
    )

    await update.message.reply_text(message, parse_mode='Markdown')


async def handle_button_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text from menu buttons."""
    text = update.message.text
    user_id = update.effective_user.id
    lang = Teacher.get_language(user_id)

    from handlers.attendance import checkin_command, checkout_command

    if get_message(lang, 'btn_checkin') in text:
        await checkin_command(update, context)
    elif get_message(lang, 'btn_checkout') in text:
        await checkout_command(update, context)
    elif get_message(lang, 'btn_status') in text:
        await status_command(update, context)
    elif get_message(lang, 'btn_history') in text:
        await history_command(update, context)
    elif get_message(lang, 'btn_language') in text:
        from handlers.start import language_command
        await language_command(update, context)
    elif get_message(lang, 'btn_help') in text:
        await help_command(update, context)
    elif get_message(lang, 'btn_admin') in text:
        if Config.is_admin(user_id):
            from handlers.admin import admin_panel
            await admin_panel(update, context)
        else:
            message = get_message(lang, 'error_admin_only')
            await update.message.reply_text(message, parse_mode='Markdown')
    elif get_message(lang, 'btn_stats') in text:
        await stats_command(update, context)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle errors in the bot with robust error message delivery.

    FIX: Enhanced error handler that ALWAYS attempts to notify the user,
    with multiple fallback mechanisms to ensure message delivery.
    """
    # Log the error with full traceback
    logger.error("=" * 60)
    logger.error("EXCEPTION OCCURRED IN BOT")
    logger.error("=" * 60)
    logger.error(f"Exception type: {type(context.error).__name__}")
    logger.error(f"Exception message: {context.error}", exc_info=context.error)

    # Try to get update information for debugging
    if isinstance(update, Update):
        logger.error(f"Update ID: {update.update_id}")
        if update.effective_user:
            logger.error(f"User ID: {update.effective_user.id}")
            logger.error(f"Username: {update.effective_user.username}")
        if update.effective_message:
            logger.error(f"Message ID: {update.effective_message.message_id}")
            logger.error(f"Chat ID: {update.effective_message.chat_id}")
    else:
        logger.error(f"Update object type: {type(update)}")

    logger.error("=" * 60)

    # Attempt to send error message to user with multiple fallback strategies
    error_message_sent = False

    # Strategy 1: Try using effective_message
    if isinstance(update, Update) and update.effective_message:
        try:
            user_id = update.effective_user.id if update.effective_user else None

            # Try to get user's language
            lang = 'en'  # Default fallback
            if user_id:
                try:
                    lang = Teacher.get_language(user_id)
                    logger.info(f"Retrieved language for user {user_id}: {lang}")
                except Exception as lang_error:
                    logger.warning(f"Could not get user language, using default: {lang_error}")

            # Get localized error message
            try:
                message = get_message(lang, 'error_general')
            except Exception as msg_error:
                logger.warning(f"Could not get localized message: {msg_error}")
                # Hard-coded fallback messages
                fallback_messages = {
                    'en': "An error occurred while processing your request.\n\nPlease try again or contact an administrator.",
                    'ru': "Произошла ошибка при обработке вашего запроса.\n\nПопробуйте снова или обратитесь к администратору.",
                    'uz': "So'rovingizni qayta ishlashda xatolik yuz berdi.\n\nQayta urinib ko'ring yoki administratorga murojaat qiling."
                }
                message = fallback_messages.get(lang, fallback_messages['en'])

            # Attempt to send the message
            await update.effective_message.reply_text(message)
            error_message_sent = True
            logger.info(f"Error message sent successfully to user {user_id} via effective_message")

        except Exception as e:
            logger.error(f"Strategy 1 failed (effective_message): {e}")

    # Strategy 2: Try using context.bot.send_message with chat_id
    if not error_message_sent and isinstance(update, Update):
        try:
            chat_id = None
            user_id = None

            if update.effective_chat:
                chat_id = update.effective_chat.id
            if update.effective_user:
                user_id = update.effective_user.id

            if chat_id:
                # Try to get language
                lang = 'en'
                if user_id:
                    try:
                        lang = Teacher.get_language(user_id)
                    except:
                        pass

                # Get message
                try:
                    message = get_message(lang, 'error_general')
                except:
                    message = "An error occurred. Please try again."

                # Send via bot
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=message
                )
                error_message_sent = True
                logger.info(f"Error message sent successfully to chat {chat_id} via bot.send_message")

        except Exception as e:
            logger.error(f"Strategy 2 failed (bot.send_message): {e}")

    # Strategy 3: Last resort - try to send a simple message without localization
    if not error_message_sent and isinstance(update, Update):
        try:
            if update.effective_message:
                await update.effective_message.reply_text(
                    "⚠️ An error occurred. Please try again.\n\n"
                    "If the problem persists, contact an administrator."
                )
                error_message_sent = True
                logger.info("Error message sent successfully via last resort method")
        except Exception as e:
            logger.error(f"Strategy 3 failed (last resort): {e}")

    # Log final status
    if error_message_sent:
        logger.info("✅ Error message successfully delivered to user")
    else:
        logger.error("❌ CRITICAL: Failed to send error message to user through all strategies")
        logger.error("User will only see Telegram's generic error popup")


def main() -> None:
    """Start the bot."""
    logger.info("=" * 60)
    logger.info("Starting Attendance Bot...")
    logger.info("=" * 60)

    logger.info("Starting health check server on port 8080...")
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    logger.info("✅ Health check server started")

    logger.info("Validating configuration...")
    if not Config.validate():
        logger.error("Configuration validation failed. Exiting.")
        sys.exit(1)

    logger.info("Initializing database...")
    try:
        from database.db import init_database, get_db_stats
        init_database()
        stats = get_db_stats()
        logger.info(f"Database initialized successfully:")
        logger.info(f"  - Teachers: {stats['teachers']}")
        logger.info(f"  - Attendance Records: {stats['attendance_records']}")
        logger.info(f"  - Admin Logs: {stats['admin_logs']}")
        if 'notifications_total' in stats:
            logger.info(f"  - Notifications Sent: {stats['notifications_total']}")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        logger.error("Please check database permissions and configuration")
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("Configuration:")
    logger.info(f"  - School Location: ({Config.SCHOOL_LATITUDE:.6f}, {Config.SCHOOL_LONGITUDE:.6f})")
    logger.info(f"  - Check-in Radius: {Config.RADIUS_METERS}m")
    logger.info(f"  - Admin Users: {len(Config.ADMIN_USER_IDS)}")
    logger.info(f"  - Supported Languages: {', '.join(Config.SUPPORTED_LANGUAGES)}")
    logger.info(f"  - Default Language: {Config.DEFAULT_LANGUAGE}")
    logger.info(f"  - Timezone: {Config.TIMEZONE}")
    logger.info(f"  - Log Level: {Config.LOG_LEVEL}")
    logger.info(f"  - Work Hours: {Config.WORK_START_TIME} - {Config.WORK_END_TIME}")
    logger.info(f"  - Grace Period: {Config.GRACE_PERIOD_MINUTES} minutes")
    logger.info(f"  - Work Days: {Config.WORK_DAYS}")
    logger.info("=" * 60)

    logger.info("Building Telegram application...")
    application = Application.builder().token(Config.BOT_TOKEN).build()

    logger.info("Setting up scheduled notification jobs...")
    setup_notification_jobs(application)

    logger.info("Registering command handlers...")
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("myid", myid_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("stats", stats_command))

    from handlers.start import language_command, language_callback
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))

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

    from handlers.admin import admin_panel, admin_callback, view_schedule_command
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CommandHandler("schedule", view_schedule_command))
    application.add_handler(CallbackQueryHandler(admin_callback, pattern="^admin_"))

    from handlers.preferences import notifications_command
    application.add_handler(CommandHandler("notifications", notifications_command))

    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_button_text
    ))

    application.add_error_handler(error_handler)

    logger.info("All handlers registered successfully")
    logger.info("=" * 60)

    logger.info("🚀 Bot is ready! Starting polling...")
    logger.info("=" * 60)
    logger.info("✨ Features:")
    logger.info("  - Multi-language support (EN/RU/UZ)")
    logger.info("  - Persistent menu buttons")
    logger.info("  - Location-based check-in/out")
    logger.info("  - Admin panel with reports & CSV export")
    logger.info("  - Zero-downtime deployment")
    logger.info("  - Smart notification system (Phase 2)")
    logger.info("  - Late detection with grace period")
    logger.info("  - Automatic notification reminders")
    logger.info("  - Rate limiting (COMMIT 2)")
    logger.info("  - Enhanced error handling (COMMIT 3)")
    logger.info("=" * 60)
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
