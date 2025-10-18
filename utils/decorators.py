"""
Utility decorators for handlers.
Provides common functionality like weekday checks, admin verification, etc.
"""
import logging
from datetime import datetime
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

from config import Config
from database.models import Teacher
from locales import get_message

logger = logging.getLogger(__name__)


def weekday_only(func):
    """
    Decorator to restrict command to weekdays only.
    Sends a message to user if called on weekend.

    Usage:
        @weekday_only
        async def check_in(update, context):
            ...
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        # 0 = Monday, 6 = Sunday
        today = datetime.now().weekday()

        if today >= 5:  # Saturday (5) or Sunday (6)
            lang = Teacher.get_language(update.effective_user.id)
            message = get_message(lang, 'error_weekend')
            await update.message.reply_text(message, parse_mode='Markdown')
            logger.info(f"User {update.effective_user.id} tried to use {func.__name__} on weekend")
            return

        return await func(update, context, *args, **kwargs)

    return wrapper


def admin_only(func):
    """
    Decorator to restrict command to admins only.
    Sends a message to user if they're not an admin.

    Usage:
        @admin_only
        async def admin_panel(update, context):
            ...
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id

        if not Config.is_admin(user_id):
            lang = Teacher.get_language(user_id)
            message = get_message(lang, 'error_admin_only')
            await update.message.reply_text(message, parse_mode='Markdown')
            logger.warning(f"User {user_id} attempted to use admin command: {func.__name__}")
            return

        logger.info(f"Admin {user_id} using command: {func.__name__}")
        return await func(update, context, *args, **kwargs)

    return wrapper


def registered_user_only(func):
    """
    Decorator to ensure user is registered in database.
    Prompts user to use /start if not registered.

    Usage:
        @registered_user_only
        async def check_in(update, context):
            ...
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        from database.models import Teacher

        user_id = update.effective_user.id
        teacher = Teacher.get_by_id(user_id)

        if not teacher:
            # Use default language since user isn't registered
            message = get_message('en', 'error_not_registered')
            await update.message.reply_text(message, parse_mode='Markdown')
            logger.warning(f"Unregistered user {user_id} tried to use {func.__name__}")
            return

        return await func(update, context, *args, **kwargs)

    return wrapper
