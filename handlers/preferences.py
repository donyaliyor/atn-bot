"""
User notification preference management.
Allows users to enable/disable notifications and view their settings.

PHASE 2: Smart notification preferences.
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import Config
from database.models import Teacher
from locales import get_message

logger = logging.getLogger(__name__)


async def notifications_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /notifications command.
    Shows current notification settings and allows user to toggle on/off.

    Args:
        update: Telegram update object
        context: Callback context
    """
    user = update.effective_user
    logger.info(f"User {user.id} requested notification settings")

    # Get user's language
    lang = Teacher.get_language(user.id)

    # Get current notification preference
    teacher = Teacher.get_by_id(user.id)

    if not teacher:
        message = get_message(lang, 'error_not_registered')
        await update.message.reply_text(message, parse_mode='Markdown')
        return

    current_state = teacher.get('notification_enabled', 1)  # Default: enabled

    # Create toggle button
    status_text = 'enabled' if current_state else 'disabled'
    button_text = 'Disable Notifications' if current_state else 'Enable Notifications'

    keyboard = [[
        InlineKeyboardButton(
            button_text,
            callback_data=f"notif_toggle_{user.id}"
        )
    ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Get notification schedule info for display
    notification_times = Config.get_notification_times()

    message = get_message(
        lang,
        'notification_settings',
        status=status_text,
        morning_time=notification_times['morning_reminder'].strftime('%H:%M'),
        late_time=notification_times['late_warning'].strftime('%H:%M'),
        checkout_time=notification_times['checkout_reminder'].strftime('%H:%M'),
        forgotten_time=notification_times['forgotten_checkout'].strftime('%H:%M')
    )

    await update.message.reply_text(
        message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def notification_toggle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle notification toggle button callback.
    Toggles notification preference for the user.

    Args:
        update: Telegram update object
        context: Callback context
    """
    query = update.callback_query
    user = query.from_user

    logger.info(f"User {user.id} toggling notification preference")

    # Get user's language
    lang = Teacher.get_language(user.id)

    # Answer the callback query immediately
    await query.answer()

    # Get current preference
    teacher = Teacher.get_by_id(user.id)

    if not teacher:
        await query.edit_message_text(
            get_message(lang, 'error_not_registered'),
            parse_mode='Markdown'
        )
        return

    current_state = teacher.get('notification_enabled', 1)
    new_state = not current_state

    # Update preference in database
    success = Teacher.set_notification_preference(user.id, new_state)

    if success:
        status_text = 'enabled' if new_state else 'disabled'
        message = get_message(
            lang,
            'notification_toggled',
            status=status_text
        )

        # Add information about what this means
        if new_state:
            message += "\n\n" + get_message(lang, 'notification_enabled')
        else:
            message += "\n\n" + get_message(lang, 'notification_disabled')

        await query.edit_message_text(message, parse_mode='Markdown')

        logger.info(f"Notifications {status_text} for user {user.id}")
    else:
        # Error updating preference
        message = get_message(lang, 'error_general')
        await query.edit_message_text(message, parse_mode='Markdown')

        logger.error(f"Failed to toggle notifications for user {user.id}")
