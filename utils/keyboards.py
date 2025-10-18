"""
Keyboard builders for bot interface.
Creates reply and inline keyboards for user interaction.
Provides persistent menu keyboards and location sharing keyboards.
"""
import logging
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from locales import get_message

logger = logging.getLogger(__name__)


def get_location_keyboard(lang: str = 'en') -> ReplyKeyboardMarkup:
    """
    Create a keyboard with location sharing button.
    Used for check-in and check-out operations.

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


def get_main_menu_keyboard(lang: str = 'en') -> ReplyKeyboardMarkup:
    """
    Create main menu keyboard with common actions.
    This keyboard stays visible at the bottom of the chat,
    providing quick access to all main bot functions.

    Args:
        lang: User's language code

    Returns:
        ReplyKeyboardMarkup: Main menu keyboard

    Usage:
        await update.message.reply_text(
            "Welcome!",
            reply_markup=get_main_menu_keyboard(lang)
        )
    """
    keyboard = [
        [
            KeyboardButton("✅ " + get_message(lang, 'btn_checkin')),
            KeyboardButton("🚪 " + get_message(lang, 'btn_checkout'))
        ],
        [
            KeyboardButton("📊 " + get_message(lang, 'btn_status')),
            KeyboardButton("📜 " + get_message(lang, 'btn_history'))
        ],
        [
            KeyboardButton("🌍 " + get_message(lang, 'btn_language')),
            KeyboardButton("❓ " + get_message(lang, 'btn_help'))
        ]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


def get_admin_keyboard(lang: str = 'en') -> ReplyKeyboardMarkup:
    """
    Create admin menu keyboard with admin-specific actions.
    Includes both user and admin functions.

    Args:
        lang: User's language code

    Returns:
        ReplyKeyboardMarkup: Admin menu keyboard

    Usage:
        await update.message.reply_text(
            "Admin Menu:",
            reply_markup=get_admin_keyboard(lang)
        )
    """
    keyboard = [
        [
            KeyboardButton("✅ " + get_message(lang, 'btn_checkin')),
            KeyboardButton("🚪 " + get_message(lang, 'btn_checkout'))
        ],
        [
            KeyboardButton("📊 " + get_message(lang, 'btn_status')),
            KeyboardButton("📜 " + get_message(lang, 'btn_history'))
        ],
        [
            KeyboardButton("🔐 " + get_message(lang, 'btn_admin')),
            KeyboardButton("📈 " + get_message(lang, 'btn_stats'))
        ],
        [
            KeyboardButton("🌍 " + get_message(lang, 'btn_language')),
            KeyboardButton("❓ " + get_message(lang, 'btn_help'))
        ]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )
