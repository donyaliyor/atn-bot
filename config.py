"""
Configuration management for the attendance bot.
Loads and validates environment variables.
"""
import os
import logging
from typing import List
from datetime import time, datetime
from pathlib import Path
from dotenv import load_dotenv
import pytz

load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Application configuration with validation."""

    BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')

    SCHOOL_LATITUDE: float = float(os.getenv('SCHOOL_LATITUDE', '41.2995'))
    SCHOOL_LONGITUDE: float = float(os.getenv('SCHOOL_LONGITUDE', '69.2401'))
    RADIUS_METERS: int = int(os.getenv('RADIUS_METERS', '50'))

    ADMIN_USER_IDS: List[int] = [
        int(user_id.strip())
        for user_id in os.getenv('ADMIN_USER_IDS', '').split(',')
        if user_id.strip()
    ]

    DEFAULT_LANGUAGE: str = os.getenv('DEFAULT_LANGUAGE', 'uz')
    SUPPORTED_LANGUAGES: List[str] = ['en', 'ru', 'uz']
    TIMEZONE: str = os.getenv('TIMEZONE', 'Asia/Tashkent')

    @staticmethod
    def _get_db_path() -> str:
        """Get database path with proper priority."""
        if env_path := os.getenv('DB_PATH'):
            return env_path

        prod_dir = Path('/app/data')
        if prod_dir.exists() and prod_dir.is_dir():
            return str(prod_dir / 'attendance.db')

        local_dir = Path('./data')
        local_dir.mkdir(exist_ok=True)
        return str(local_dir / 'attendance.db')

    DB_PATH: str = _get_db_path.__func__()

    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')

    WORK_START_TIME: str = os.getenv('WORK_START_TIME', '08:00')
    WORK_END_TIME: str = os.getenv('WORK_END_TIME', '17:00')
    GRACE_PERIOD_MINUTES: int = int(os.getenv('GRACE_PERIOD_MINUTES', '15'))

    WORK_DAYS: List[int] = [
        int(day.strip())
        for day in os.getenv('WORK_DAYS', '1,2,3,4,5').split(',')
        if day.strip()
    ]

    MORNING_REMINDER_MINUTES_BEFORE: int = int(os.getenv('MORNING_REMINDER_MINUTES_BEFORE', '15'))
    LATE_WARNING_MINUTES_AFTER: int = int(os.getenv('LATE_WARNING_MINUTES_AFTER', '15'))
    CHECKOUT_REMINDER_MINUTES_BEFORE: int = int(os.getenv('CHECKOUT_REMINDER_MINUTES_BEFORE', '15'))
    FORGOTTEN_CHECKOUT_MINUTES_AFTER: int = int(os.getenv('FORGOTTEN_CHECKOUT_MINUTES_AFTER', '30'))

    @classmethod
    def get_timezone(cls) -> pytz.timezone:
        """
        Get pytz timezone object for the configured timezone.

        Returns:
            pytz.timezone: Timezone object for Asia/Tashkent or configured TZ
        """
        try:
            return pytz.timezone(cls.TIMEZONE)
        except Exception as e:
            logger.error(f"Error loading timezone {cls.TIMEZONE}: {e}")
            logger.warning("Falling back to UTC")
            return pytz.UTC

    @classmethod
    def now(cls) -> datetime:
        """
        Get current datetime in the configured timezone.

        CRITICAL: This replaces all datetime.now() calls to ensure timezone awareness.

        Returns:
            datetime: Current time in Asia/Tashkent (or configured timezone)

        Example:
            >>> from config import Config
            >>> current_time = Config.now()
            >>> print(current_time)  # 2025-10-20 07:47:15+05:00
        """
        tz = cls.get_timezone()
        return datetime.now(tz)

    @classmethod
    def today(cls):
        """
        Get today's date in the configured timezone.

        Returns:
            date: Today's date in the configured timezone
        """
        return cls.now().date()

    @classmethod
    def validate(cls) -> bool:
        """Validate configuration."""
        if not cls.BOT_TOKEN:
            logger.error("BOT_TOKEN is required")
            return False

        if not cls.ADMIN_USER_IDS:
            logger.warning("No admin users configured")

        if cls.DEFAULT_LANGUAGE not in cls.SUPPORTED_LANGUAGES:
            logger.error(f"Invalid default language: {cls.DEFAULT_LANGUAGE}")
            return False

        logger.info("Configuration validated successfully")
        logger.info(f"Timezone: {cls.TIMEZONE}")
        logger.info(f"Current time: {cls.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
        return True

    @classmethod
    def get_work_start_time(cls) -> time:
        """Parse and return work start time."""
        hour, minute = map(int, cls.WORK_START_TIME.split(':'))
        return time(hour=hour, minute=minute)

    @classmethod
    def get_work_end_time(cls) -> time:
        """Parse and return work end time."""
        hour, minute = map(int, cls.WORK_END_TIME.split(':'))
        return time(hour=hour, minute=minute)

    @classmethod
    def get_schedule_summary(cls) -> str:
        """Get human-readable schedule summary."""
        day_names = {1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat', 7: 'Sun'}
        work_days_str = ', '.join([day_names.get(d, str(d)) for d in sorted(cls.WORK_DAYS)])

        return (
            f"Work Schedule:\n"
            f"Hours: {cls.WORK_START_TIME} - {cls.WORK_END_TIME}\n"
            f"Days: {work_days_str}\n"
            f"Grace Period: {cls.GRACE_PERIOD_MINUTES} minutes"
        )

    @classmethod
    def get_notification_times(cls) -> dict:
        """Get notification times calculated from work schedule."""
        start_time = cls.get_work_start_time()
        end_time = cls.get_work_end_time()

        start_minutes = start_time.hour * 60 + start_time.minute
        end_minutes = end_time.hour * 60 + end_time.minute

        morning_minutes = start_minutes - cls.MORNING_REMINDER_MINUTES_BEFORE
        late_minutes = start_minutes + cls.LATE_WARNING_MINUTES_AFTER
        checkout_minutes = end_minutes - cls.CHECKOUT_REMINDER_MINUTES_BEFORE
        forgotten_minutes = end_minutes + cls.FORGOTTEN_CHECKOUT_MINUTES_AFTER

        def minutes_to_time(total_minutes: int) -> time:
            total_minutes = total_minutes % (24 * 60)
            return time(hour=total_minutes // 60, minute=total_minutes % 60)

        return {
            'morning_reminder': minutes_to_time(morning_minutes),
            'late_warning': minutes_to_time(late_minutes),
            'checkout_reminder': minutes_to_time(checkout_minutes),
            'forgotten_checkout': minutes_to_time(forgotten_minutes)
        }


if not Config.validate():
    logger.warning("Configuration validation failed - bot may not work correctly")
