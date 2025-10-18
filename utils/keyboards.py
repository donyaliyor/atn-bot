"""
Keyboard builders for bot interface.
Creates reply and inline keyboards for user interaction.
"""
import logging
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from locales import get_message

logger = logging.getLogger(__name__)


def get_location_keyboard(lang: str = 'en') -> ReplyKeyboardMarkup:
    """
    Create a keyboard with location sharing button.

    Args:
        lang: User's language code

    Returns:
        ReplyKeyboardMarkup: Keyboard with location button

    Usage:
        await update.message.reply_text(
            "Share your location:",
            reply_markup=get_location_keyboard(lang)
        )
    """
    keyboard = [
        [KeyboardButton(
            get_message(lang, 'btn_share_location'),
            request_location=True
        )],
        [KeyboardButton(get_message(lang, 'btn_cancel'))]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    """
    Remove custom keyboard.

    Returns:
        ReplyKeyboardRemove: Object to remove keyboard

    Usage:
        await update.message.reply_text(
            "Done!",
            reply_markup=remove_keyboard()
        )
    """
    return ReplyKeyboardRemove()


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Create main menu keyboard with common actions.

    Returns:
        ReplyKeyboardMarkup: Main menu keyboard
    """
    keyboard = [
        [KeyboardButton("✅ Check In"), KeyboardButton("🚪 Check Out")],
        [KeyboardButton("📊 My Status"), KeyboardButton("📜 History")],
        [KeyboardButton("❓ Help")]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )
