"""
User notification preference management.
Allows users to view their notification settings.

PHASE 2: Notifications are always enabled for all users.
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from config import Config
from database.models import Teacher
from locales import get_message

logger = logging.getLogger(__name__)


async def notifications_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /notifications command.
    Shows notification schedule information (view-only, no toggle button).

    Args:
        update: Telegram update object
        context: Callback context
    """
    user = update.effective_user
    logger.info(f"User {user.id} requested notification settings")

    # Get user's language
    lang = Teacher.get_language(user.id)

    # Verify user is registered
    teacher = Teacher.get_by_id(user.id)

    if not teacher:
        message = get_message(lang, 'error_not_registered')
        await update.message.reply_text(message, parse_mode='Markdown')
        return

    # Get notification schedule info for display
    notification_times = Config.get_notification_times()

    message = get_message(
        lang,
        'notification_settings',
        status='enabled',  # Always enabled
        morning_time=notification_times['morning_reminder'].strftime('%H:%M'),
        late_time=notification_times['late_warning'].strftime('%H:%M'),
        checkout_time=notification_times['checkout_reminder'].strftime('%H:%M'),
        forgotten_time=notification_times['forgotten_checkout'].strftime('%H:%M')
    )

    # Send message WITHOUT button (removed InlineKeyboardMarkup)
    await update.message.reply_text(
        message,
        parse_mode='Markdown'
    )
