"""
Configuration management for Attendance Bot.
Loads and validates environment variables.
"""
import os
import logging
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file (local development only)
load_dotenv()

# Configure logging at module level
logger = logging.getLogger(__name__)


class Config:
    """Application configuration with validation."""

    # Bot Configuration
    BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')

    # School Location
    SCHOOL_LATITUDE: float = float(os.getenv('SCHOOL_LATITUDE', '41.2995'))
    SCHOOL_LONGITUDE: float = float(os.getenv('SCHOOL_LONGITUDE', '69.2401'))
    RADIUS_METERS: int = int(os.getenv('RADIUS_METERS', '50'))

    # Admin Configuration
    ADMIN_USER_IDS: List[int] = [
        int(user_id.strip())
        for user_id in os.getenv('ADMIN_USER_IDS', '').split(',')
        if user_id.strip()
    ]

    # Application Settings
    DEFAULT_LANGUAGE: str = os.getenv('DEFAULT_LANGUAGE', 'en')
    SUPPORTED_LANGUAGES: List[str] = ['en', 'ru', 'uz']
    TIMEZONE: str = os.getenv('TIMEZONE', 'Asia/Tashkent')

    # Database path - Use mounted volume in production
    # Fly.io will have /app/data mounted, local will use current directory
    DB_PATH: str = os.getenv('DB_PATH', '/app/data/attendance.db' if os.path.exists('/app/data') else 'attendance.db')

    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')

    @classmethod
    def validate(cls) -> bool:
        """
        Validate critical configuration values.

        Returns:
            bool: True if configuration is valid, False otherwise
        """
        if not cls.BOT_TOKEN:
            logger.error("BOT_TOKEN is not set in environment variables")
            return False

        if cls.RADIUS_METERS <= 0:
            logger.error(f"Invalid RADIUS_METERS: {cls.RADIUS_METERS}")
            return False

        if cls.DEFAULT_LANGUAGE not in cls.SUPPORTED_LANGUAGES:
            logger.warning(
                f"DEFAULT_LANGUAGE '{cls.DEFAULT_LANGUAGE}' not in "
                f"supported languages: {cls.SUPPORTED_LANGUAGES}"
            )

        logger.info("Configuration validated successfully")
        return True

    @classmethod
    def is_admin(cls, user_id: int) -> bool:
        """
        Check if a user is an admin.

        Args:
            user_id: Telegram user ID

        Returns:
            bool: True if user is admin, False otherwise
        """
        return user_id in cls.ADMIN_USER_IDS


# Validate configuration on module import
if not Config.validate():
    logger.warning("Configuration validation failed - bot may not work correctly")
