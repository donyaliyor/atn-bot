"""
Internationalization (i18n) utilities.
Provides easy access to translations.
"""
import logging
from typing import Dict, Any

from locales import en, ru, uz

logger = logging.getLogger(__name__)

# Language modules mapping
LANGUAGES = {
    'en': en,
    'ru': ru,
    'uz': uz
}

# Language display names
LANGUAGE_NAMES = {
    'en': '🇬🇧 English',
    'ru': '🇷🇺 Русский',
    'uz': '🇺🇿 O\'zbek'
}


def get_message(language: str, key: str, **kwargs) -> str:
    """
    Get a translated message.

    Args:
        language: Language code ('en', 'ru', 'uz')
        key: Message key
        **kwargs: Format parameters for the message

    Returns:
        str: Translated and formatted message

    Example:
        >>> msg = get_message('en', 'welcome', first_name='John', radius=50)
        >>> print(msg)
    """
    # Fallback to English if language not supported
    if language not in LANGUAGES:
        logger.warning(f"Unsupported language '{language}', falling back to 'en'")
        language = 'en'

    lang_module = LANGUAGES[language]

    # Get message
    try:
        message_template = lang_module.MESSAGES.get(key)

        if message_template is None:
            logger.error(f"Message key '{key}' not found in '{language}' translations")
            # Try fallback to English
            if language != 'en':
                message_template = en.MESSAGES.get(key)

            if message_template is None:
                return f"[Missing translation: {key}]"

        # Format message with parameters
        if kwargs:
            try:
                return message_template.format(**kwargs)
            except KeyError as e:
                logger.error(f"Missing format parameter {e} for key '{key}'")
                return message_template

        return message_template

    except Exception as e:
        logger.error(f"Error getting message '{key}' in '{language}': {e}")
        return f"[Translation error: {key}]"


def get_language_name(language: str) -> str:
    """
    Get display name for a language.

    Args:
        language: Language code

    Returns:
        str: Display name with flag emoji
    """
    return LANGUAGE_NAMES.get(language, language)


def get_available_languages() -> Dict[str, str]:
    """
    Get all available languages.

    Returns:
        Dict[str, str]: Mapping of language codes to display names
    """
    return LANGUAGE_NAMES.copy()
