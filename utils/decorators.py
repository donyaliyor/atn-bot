"""
Utility decorators for handlers.
Provides common functionality like weekday checks, admin verification, rate limiting, etc.

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

_rate_limit_store = {}


def rate_limit(seconds: int):
    """
    Decorator to rate limit commands per user.

    Prevents users from spamming commands by enforcing a minimum time between calls.
    Uses in-memory storage to track last command time per user.

    Args:
        seconds: Minimum seconds between command calls

    Usage:
        @rate_limit(seconds=2)
        async def some_command(update, context):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = update.effective_user.id
            now = datetime.now().timestamp()

            if user_id in _rate_limit_store:
                last_used = _rate_limit_store[user_id]
                elapsed = now - last_used

                if elapsed < seconds:
                    remaining = int(seconds - elapsed) + 1

                    lang = Teacher.get_language(user_id)
                    message = get_message(
                        lang,
                        'error_rate_limit',
                        seconds=remaining
                    )

                    await update.message.reply_text(message, parse_mode='Markdown')
                    logger.info(
                        f"Rate limit hit for user {user_id} on {func.__name__}, "
                        f"{remaining}s remaining"
                    )
                    return

            _rate_limit_store[user_id] = now
            return await func(update, context, *args, **kwargs)

        return wrapper
    return decorator


def weekday_only(func):
    """
    Decorator to restrict command to weekdays only.
    Sends a message to user if called on weekend.
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        today = datetime.now().weekday()

        if today >= 5:
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
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        from database.models import Teacher

        user_id = update.effective_user.id
        teacher = Teacher.get_by_id(user_id)

        if not teacher:
            message = get_message('en', 'error_not_registered')
            await update.message.reply_text(message, parse_mode='Markdown')
            logger.warning(f"Unregistered user {user_id} tried to use {func.__name__}")
            return

        return await func(update, context, *args, **kwargs)

    return wrapper
