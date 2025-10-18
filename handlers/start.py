"""
Start and language selection handlers.
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import Config
from database.models import Teacher
from locales import get_message, get_available_languages

logger = logging.getLogger(__name__)


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /language command.
    Shows language selection buttons.

    Args:
        update: Telegram update object
        context: Callback context
    """
    user = update.effective_user
    logger.info(f"User {user.id} requested language selection")

    # Get user's current language
    current_lang = Teacher.get_language(user.id)

    # Create inline keyboard with language options
    keyboard = [
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = get_message(current_lang, 'language_select')

    await update.message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle language selection callback.
    Updates user's language preference.

    Args:
        update: Telegram update object
        context: Callback context
    """
    query = update.callback_query
    user = query.from_user

    # Extract language code from callback data
    language = query.data.split('_')[1]  # "lang_en" -> "en"

    logger.info(f"User {user.id} selected language: {language}")

    # Update language in database
    success = Teacher.set_language(user.id, language)

    if success:
        # Answer callback query
        await query.answer()

        # Send confirmation in new language
        confirmation = get_message(language, 'language_changed')
        await query.edit_message_text(
            confirmation,
            parse_mode='Markdown'
        )

        logger.info(f"Language changed to {language} for user {user.id}")
    else:
        await query.answer("Error changing language. Please try again.", show_alert=True)
        logger.error(f"Failed to change language for user {user.id}")
