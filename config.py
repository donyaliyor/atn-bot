"""
Configuration management for Attendance Bot.
Loads and validates environment variables.

"""
import os
import logging
from typing import List, Tuple
from datetime import time, datetime
from dotenv import load_dotenv

# Load environment variables from .env file (local development only)
load_dotenv()

# Configure logging at module level
logger = logging.getLogger(__name__)


class Config:
    """Application configuration with validation."""

    # ========================================================================
    # PHASE 1: Original Configuration
    # ========================================================================

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
    DEFAULT_LANGUAGE: str = os.getenv('DEFAULT_LANGUAGE', 'uz')
    SUPPORTED_LANGUAGES: List[str] = ['en', 'ru', 'uz']
    TIMEZONE: str = os.getenv('TIMEZONE', 'Asia/Tashkent')

    # Database path - Use mounted volume in production
    DB_PATH: str = os.getenv('DB_PATH', '/app/data/attendance.db' if os.path.exists('/app/data') else 'attendance.db')

    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')

    # ========================================================================
    # PHASE 2: Work Schedule Configuration
    # ========================================================================

    # Work Schedule Times (HH:MM format)
    WORK_START_TIME: str = os.getenv('WORK_START_TIME', '08:00')
    WORK_END_TIME: str = os.getenv('WORK_END_TIME', '17:00')

    # Grace period in minutes (late if beyond this)
    GRACE_PERIOD_MINUTES: int = int(os.getenv('GRACE_PERIOD_MINUTES', '15'))

    # Work days (1=Monday, 7=Sunday)
    WORK_DAYS: List[int] = [
        int(day.strip())
        for day in os.getenv('WORK_DAYS', '1,2,3,4,5').split(',')
        if day.strip()
    ]

    # ========================================================================
    # PHASE 2: Notification Configuration
    # ========================================================================

    # Notification timing (minutes before/after work times)
    MORNING_REMINDER_MINUTES_BEFORE: int = int(os.getenv('MORNING_REMINDER_MINUTES_BEFORE', '15'))
    LATE_WARNING_MINUTES_AFTER: int = int(os.getenv('LATE_WARNING_MINUTES_AFTER', '15'))
    CHECKOUT_REMINDER_MINUTES_BEFORE: int = int(os.getenv('CHECKOUT_REMINDER_MINUTES_BEFORE', '15'))
    FORGOTTEN_CHECKOUT_MINUTES_AFTER: int = int(os.getenv('FORGOTTEN_CHECKOUT_MINUTES_AFTER', '30'))

    # ========================================================================
    # Helper Methods
    # ========================================================================

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

        # PHASE 2: Validate work schedule
        if not cls._validate_time_format(cls.WORK_START_TIME):
            logger.error(f"Invalid WORK_START_TIME format: {cls.WORK_START_TIME}")
            return False

        if not cls._validate_time_format(cls.WORK_END_TIME):
            logger.error(f"Invalid WORK_END_TIME format: {cls.WORK_END_TIME}")
            return False

        if cls.GRACE_PERIOD_MINUTES < 0 or cls.GRACE_PERIOD_MINUTES > 60:
            logger.warning(f"Unusual grace period: {cls.GRACE_PERIOD_MINUTES} minutes")

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

    # ========================================================================
    # PHASE 2: Work Schedule Helpers
    # ========================================================================

    @classmethod
    def _validate_time_format(cls, time_str: str) -> bool:
        """
        Validate time string format (HH:MM).

        Args:
            time_str: Time string to validate

        Returns:
            bool: True if valid format
        """
        try:
            hours, minutes = map(int, time_str.split(':'))
            return 0 <= hours <= 23 and 0 <= minutes <= 59
        except:
            return False

    @classmethod
    def get_work_start_time(cls) -> time:
        """
        Get work start time as datetime.time object.

        Returns:
            time: Work start time
        """
        try:
            hours, minutes = map(int, cls.WORK_START_TIME.split(':'))
            return time(hour=hours, minute=minutes)
        except:
            logger.error(f"Error parsing WORK_START_TIME: {cls.WORK_START_TIME}")
            return time(hour=8, minute=0)  # Fallback to 8:00 AM

    @classmethod
    def get_work_end_time(cls) -> time:
        """
        Get work end time as datetime.time object.

        Returns:
            time: Work end time
        """
        try:
            hours, minutes = map(int, cls.WORK_END_TIME.split(':'))
            return time(hour=hours, minute=minutes)
        except:
            logger.error(f"Error parsing WORK_END_TIME: {cls.WORK_END_TIME}")
            return time(hour=17, minute=0)  # Fallback to 5:00 PM

    @classmethod
    def is_working_day(cls, day_number: int) -> bool:
        """
        Check if a day number is a working day.

        Args:
            day_number: Day number (1=Monday, 7=Sunday)

        Returns:
            bool: True if working day
        """
        return day_number in cls.WORK_DAYS

    @classmethod
    def get_schedule_summary(cls) -> str:
        """
        Get human-readable schedule summary.

        Returns:
            str: Schedule summary
        """
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
        """
        Get all notification times calculated from work schedule.

        Returns:
            dict: Notification times
        """
        start_time = cls.get_work_start_time()
        end_time = cls.get_work_end_time()

        # Calculate notification times
        start_minutes = start_time.hour * 60 + start_time.minute
        end_minutes = end_time.hour * 60 + end_time.minute

        morning_minutes = start_minutes - cls.MORNING_REMINDER_MINUTES_BEFORE
        late_minutes = start_minutes + cls.LATE_WARNING_MINUTES_AFTER
        checkout_minutes = end_minutes - cls.CHECKOUT_REMINDER_MINUTES_BEFORE
        forgotten_minutes = end_minutes + cls.FORGOTTEN_CHECKOUT_MINUTES_AFTER

        def minutes_to_time(total_minutes: int) -> time:
            """Convert total minutes to time object."""
            # Handle day overflow
            total_minutes = total_minutes % (24 * 60)
            return time(hour=total_minutes // 60, minute=total_minutes % 60)

        return {
            'morning_reminder': minutes_to_time(morning_minutes),
            'late_warning': minutes_to_time(late_minutes),
            'checkout_reminder': minutes_to_time(checkout_minutes),
            'forgotten_checkout': minutes_to_time(forgotten_minutes)
        }


# Validate configuration on module import
if not Config.validate():
    logger.warning("Configuration validation failed - bot may not work correctly")
