"""
Start and language selection handlers.
Handles bot initialization, welcome messages, and language selection.
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import Config
from database.models import Teacher
from locales import get_message, get_available_languages
from utils.keyboards import get_main_menu_keyboard

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /start command.
    Sends a welcome message to the user, registers them in database,
    and shows the main menu keyboard.

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

    # Send welcome message with main menu keyboard
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
    Updates user's language preference with visual feedback.

    Args:
        update: Telegram update object
        context: Callback context
    """
    query = update.callback_query
    user = query.from_user

    # Extract language code from callback data
    language = query.data.split('_')[1]  # "lang_en" -> "en"

    logger.info(f"User {user.id} selected language: {language}")

    # Show loading state immediately
    await query.answer(
        get_message(language, 'language_changing'),
        show_alert=False
    )

    # Update language in database
    success = Teacher.set_language(user.id, language)

    if success:
        # Get confirmation message in new language
        confirmation = get_message(language, 'language_changed')

        # Get welcome message in new language
        welcome_msg = get_message(
            language,
            'welcome',
            first_name=user.first_name,
            radius=Config.RADIUS_METERS,
            user_id=user.id,
            full_name=f"{user.first_name} {user.last_name or ''}".strip()
        )

        # Edit message with confirmation and instructions
        full_message = f"{confirmation}\n\n{welcome_msg}"

        await query.edit_message_text(
            full_message,
            parse_mode='Markdown'
        )

        # Send new menu keyboard with updated language
        await query.message.reply_text(
            get_message(language, 'menu_updated'),
            reply_markup=get_main_menu_keyboard(language),
            parse_mode='Markdown'
        )

        logger.info(f"Language changed to {language} for user {user.id}")
    else:
        # Show error alert
        await query.answer(
            get_message(language, 'error_general'),
            show_alert=True
        )
        logger.error(f"Failed to change language for user {user.id}")
