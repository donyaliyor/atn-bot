"""
Work schedule operations and notification tracking.
Schedule configuration comes from environment variables (Config).
Database only tracks notification logs.

PHASE 2: Config-based schedule (no database storage needed).
"""
import logging
from datetime import datetime, date, time, timedelta
from typing import Optional, List, Dict, Any, Tuple

from database.db import get_db
from config import Config

logger = logging.getLogger(__name__)


class WorkSchedule:
    """
    Work schedule operations using Config-based settings.
    No database storage - all schedule settings come from environment variables.
    """

    @staticmethod
    def is_working_day(check_date: Optional[date] = None) -> bool:
        """
        Check if given date is a working day based on Config.

        Args:
            check_date: Date to check (default: today)

        Returns:
            bool: True if working day
        """
        try:
            if check_date is None:
                check_date = date.today()

            # Python weekday: 0=Monday, 6=Sunday
            # Our format: 1=Monday, 7=Sunday
            day_number = check_date.weekday() + 1

            is_working = Config.is_working_day(day_number)
            logger.debug(
                f"Date {check_date} (day {day_number}) is "
                f"{'working' if is_working else 'non-working'}"
            )

            return is_working

        except Exception as e:
            logger.error(f"Error checking working day: {e}")
            # Fallback to weekday check
            return check_date.weekday() < 5

    @staticmethod
    def is_late_checkin(checkin_time: datetime) -> Tuple[bool, int]:
        """
        Check if check-in time is late based on Config schedule and grace period.

        Args:
            checkin_time: Check-in timestamp

        Returns:
            Tuple[bool, int]: (is_late, minutes_late)
                - is_late: True if beyond grace period
                - minutes_late: Number of minutes late (0 if on time)
        """
        try:
            # Get schedule from Config
            start_time = Config.get_work_start_time()
            grace_period = Config.GRACE_PERIOD_MINUTES

            # Create datetime for scheduled start time on same day
            scheduled_start = checkin_time.replace(
                hour=start_time.hour,
                minute=start_time.minute,
                second=0,
                microsecond=0
            )

            # Add grace period
            grace_deadline = scheduled_start + timedelta(minutes=grace_period)

            # Calculate difference
            if checkin_time <= grace_deadline:
                # On time or within grace period
                return False, 0
            else:
                # Late - calculate how many minutes late
                late_by = checkin_time - grace_deadline
                minutes_late = int(late_by.total_seconds() / 60)

                logger.info(
                    f"Late check-in detected: {checkin_time.strftime('%H:%M:%S')} "
                    f"(deadline: {grace_deadline.strftime('%H:%M:%S')}, {minutes_late}min late)"
                )

                return True, minutes_late

        except Exception as e:
            logger.error(f"Error checking late check-in: {e}")
            return False, 0

    @staticmethod
    def get_checkin_status(checkin_time: datetime) -> str:
        """
        Get check-in status classification.

        Args:
            checkin_time: Check-in timestamp

        Returns:
            str: Status - 'on_time', 'late', or 'very_late'
        """
        is_late, minutes_late = WorkSchedule.is_late_checkin(checkin_time)

        if not is_late:
            return 'on_time'
        elif minutes_late <= 30:
            return 'late'
        else:
            return 'very_late'

    @staticmethod
    def should_send_reminder(current_time: datetime, reminder_type: str) -> bool:
        """
        Determine if a specific reminder should be sent at current time.

        Args:
            current_time: Current timestamp
            reminder_type: Type of reminder ('morning', 'late', 'checkout', 'forgotten')

        Returns:
            bool: True if reminder should be sent
        """
        try:
            # Only send on working days
            if not WorkSchedule.is_working_day(current_time.date()):
                logger.debug(f"Not a working day, skipping {reminder_type} reminder")
                return False

            # Get notification times from Config
            notification_times = Config.get_notification_times()

            if reminder_type not in notification_times:
                logger.warning(f"Unknown reminder type: {reminder_type}")
                return False

            target_time = notification_times[reminder_type]

            # Check if current time matches target time (within 1 minute)
            current_minutes = current_time.hour * 60 + current_time.minute
            target_minutes = target_time.hour * 60 + target_time.minute

            should_send = abs(current_minutes - target_minutes) <= 1

            if should_send:
                logger.info(
                    f"Time to send {reminder_type} reminder at "
                    f"{current_time.strftime('%H:%M')}"
                )

            return should_send

        except Exception as e:
            logger.error(f"Error checking reminder time: {e}")
            return False

    @staticmethod
    def get_schedule_info() -> Dict[str, Any]:
        """
        Get formatted schedule information for display from Config.

        Returns:
            Dict: Formatted schedule information
        """
        try:
            notification_times = Config.get_notification_times()

            return {
                'start_time': Config.WORK_START_TIME,
                'end_time': Config.WORK_END_TIME,
                'grace_period': Config.GRACE_PERIOD_MINUTES,
                'work_days': Config.WORK_DAYS,
                'work_days_text': ', '.join([
                    {1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat', 7: 'Sun'}[d]
                    for d in sorted(Config.WORK_DAYS)
                ]),
                'notification_times': {
                    'morning': notification_times['morning_reminder'].strftime('%H:%M'),
                    'late': notification_times['late_warning'].strftime('%H:%M'),
                    'checkout': notification_times['checkout_reminder'].strftime('%H:%M'),
                    'forgotten': notification_times['forgotten_checkout'].strftime('%H:%M')
                },
                'summary': Config.get_schedule_summary()
            }

        except Exception as e:
            logger.error(f"Error getting schedule info: {e}")
            return {
                'start_time': 'N/A',
                'end_time': 'N/A',
                'grace_period': 0,
                'work_days_text': 'N/A',
                'summary': 'Error loading schedule'
            }

    @staticmethod
    def is_within_work_hours(check_time: Optional[datetime] = None) -> bool:
        """
        Check if given time is within work hours.

        Args:
            check_time: Time to check (default: now)

        Returns:
            bool: True if within work hours
        """
        try:
            if check_time is None:
                check_time = datetime.now()

            # Check if it's a working day first
            if not WorkSchedule.is_working_day(check_time.date()):
                return False

            start_time = Config.get_work_start_time()
            end_time = Config.get_work_end_time()

            current_time = check_time.time()

            return start_time <= current_time <= end_time

        except Exception as e:
            logger.error(f"Error checking work hours: {e}")
            return False


class NotificationLog:
    """Notification log model for tracking sent notifications."""

    @staticmethod
    def log_notification(
        user_id: int,
        notification_type: str,
        was_delivered: bool = True,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Log a sent notification.

        Args:
            user_id: User ID who received notification
            notification_type: Type of notification sent
            was_delivered: Whether notification was successfully delivered
            error_message: Error message if delivery failed

        Returns:
            bool: True if logged successfully
        """
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO notifications_log (
                        user_id, notification_type, was_delivered, error_message
                    ) VALUES (?, ?, ?, ?)
                """, (user_id, notification_type, 1 if was_delivered else 0, error_message))

                logger.debug(
                    f"Notification logged: {notification_type} to user {user_id} "
                    f"({'delivered' if was_delivered else 'failed'})"
                )
                return True

        except Exception as e:
            logger.error(f"Error logging notification: {e}")
            return False

    @staticmethod
    def get_user_notification_count(
        user_id: int,
        notification_type: Optional[str] = None,
        days: int = 7
    ) -> int:
        """
        Get count of notifications sent to user.

        Args:
            user_id: User ID
            notification_type: Specific type (optional)
            days: Number of days to look back

        Returns:
            int: Count of notifications
        """
        try:
            with get_db() as conn:
                cursor = conn.cursor()

                if notification_type:
                    cursor.execute("""
                        SELECT COUNT(*) FROM notifications_log
                        WHERE user_id = ?
                        AND notification_type = ?
                        AND sent_at >= datetime('now', '-' || ? || ' days')
                    """, (user_id, notification_type, days))
                else:
                    cursor.execute("""
                        SELECT COUNT(*) FROM notifications_log
                        WHERE user_id = ?
                        AND sent_at >= datetime('now', '-' || ? || ' days')
                    """, (user_id, days))

                return cursor.fetchone()[0]

        except Exception as e:
            logger.error(f"Error getting notification count: {e}")
            return 0

    @staticmethod
    def get_recent_logs(limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent notification logs (for admin monitoring).

        Args:
            limit: Number of logs to retrieve

        Returns:
            List[Dict]: Recent notification logs
        """
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT
                        nl.*,
                        t.username,
                        t.first_name,
                        t.last_name
                    FROM notifications_log nl
                    LEFT JOIN teachers t ON nl.user_id = t.user_id
                    ORDER BY nl.sent_at DESC
                    LIMIT ?
                """, (limit,))

                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Error fetching notification logs: {e}")
            return []

    @staticmethod
    def get_delivery_stats(days: int = 7) -> Dict[str, Any]:
        """
        Get notification delivery statistics.

        Args:
            days: Number of days to analyze

        Returns:
            Dict: Delivery statistics
        """
        try:
            with get_db() as conn:
                cursor = conn.cursor()

                # Total sent
                cursor.execute("""
                    SELECT COUNT(*) FROM notifications_log
                    WHERE sent_at >= datetime('now', '-' || ? || ' days')
                """, (days,))
                total_sent = cursor.fetchone()[0]

                # Delivered
                cursor.execute("""
                    SELECT COUNT(*) FROM notifications_log
                    WHERE sent_at >= datetime('now', '-' || ? || ' days')
                    AND was_delivered = 1
                """, (days,))
                delivered = cursor.fetchone()[0]

                # By type
                cursor.execute("""
                    SELECT notification_type, COUNT(*) as count
                    FROM notifications_log
                    WHERE sent_at >= datetime('now', '-' || ? || ' days')
                    GROUP BY notification_type
                """, (days,))
                by_type = {row[0]: row[1] for row in cursor.fetchall()}

                return {
                    'total_sent': total_sent,
                    'delivered': delivered,
                    'failed': total_sent - delivered,
                    'delivery_rate': (delivered / total_sent * 100) if total_sent > 0 else 0,
                    'by_type': by_type
                }

        except Exception as e:
            logger.error(f"Error getting delivery stats: {e}")
            return {
                'total_sent': 0,
                'delivered': 0,
                'failed': 0,
                'delivery_rate': 0,
                'by_type': {}
            }
