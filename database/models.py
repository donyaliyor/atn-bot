"""
Database models and operations.
Provides CRUD operations for all database entities.

"""
import logging
import sqlite3
from datetime import datetime, date
from typing import Optional, List, Dict, Any

from database.db import get_db
from config import Config

logger = logging.getLogger(__name__)


class Teacher:
    """Teacher model with database operations."""

    @staticmethod
    def create_or_update(
        user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone_number: Optional[str] = None,
        language: str = 'en'
    ) -> bool:
        """Create a new teacher or update existing one."""
        try:
            with get_db() as conn:
                cursor = conn.cursor()

                is_admin = 1 if Config.is_admin(user_id) else 0

                cursor.execute("""
                    INSERT INTO teachers (
                        user_id, username, first_name, last_name,
                        phone_number, language, is_admin, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(user_id) DO UPDATE SET
                        username = excluded.username,
                        first_name = excluded.first_name,
                        last_name = excluded.last_name,
                        phone_number = excluded.phone_number,
                        language = excluded.language,
                        is_admin = excluded.is_admin,
                        updated_at = CURRENT_TIMESTAMP
                """, (user_id, username, first_name, last_name, phone_number, language, is_admin))

                logger.info(f"Teacher {user_id} ({username}) created/updated")
                return True

        except Exception as e:
            logger.error(f"Error creating/updating teacher {user_id}: {e}")
            return False

    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """Get teacher by user ID."""
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM teachers WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()

                if row:
                    return dict(row)
                return None

        except Exception as e:
            logger.error(f"Error fetching teacher {user_id}: {e}")
            return None

    @staticmethod
    def get_language(user_id: int) -> str:
        """Get user's preferred language."""
        teacher = Teacher.get_by_id(user_id)
        return teacher['language'] if teacher else Config.DEFAULT_LANGUAGE

    @staticmethod
    def set_language(user_id: int, language: str) -> bool:
        """Set user's preferred language."""
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE teachers
                    SET language = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (language, user_id))

                logger.info(f"Language set to {language} for user {user_id}")
                return True

        except Exception as e:
            logger.error(f"Error setting language for user {user_id}: {e}")
            return False

    @staticmethod
    def set_notification_preference(user_id: int, enabled: bool) -> bool:
        """Set user's notification preference."""
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE teachers
                    SET notification_enabled = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (1 if enabled else 0, user_id))

                logger.info(f"Notifications {'enabled' if enabled else 'disabled'} for user {user_id}")
                return True

        except Exception as e:
            logger.error(f"Error setting notification preference for user {user_id}: {e}")
            return False

    @staticmethod
    def get_all_active() -> List[Dict[str, Any]]:
        """Get all active teachers."""
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM teachers WHERE is_active = 1")
                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Error fetching active teachers: {e}")
            return []


class Attendance:
    """Attendance model with database operations."""

    @staticmethod
    def check_in(
        user_id: int,
        latitude: float,
        longitude: float,
        check_in_time: Optional[datetime] = None,
        late_minutes: int = 0,
        checkin_status: str = 'on_time'
    ) -> bool:
        """
        Record a check-in.

        COMMIT 2: Now catches IntegrityError for duplicate check-ins from rapid clicking.
        """
        try:
            if check_in_time is None:
                check_in_time = Config.now()  # TIMEZONE FIX: Changed from datetime.now()

            today = check_in_time.date()

            with get_db() as conn:
                cursor = conn.cursor()

                try:
                    cursor.execute("""
                        INSERT INTO attendance (
                            user_id, date, check_in_time,
                            check_in_latitude, check_in_longitude,
                            status, late_minutes, checkin_status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (user_id, today, check_in_time, latitude, longitude,
                          'checked_in', late_minutes, checkin_status))

                    logger.info(
                        f"User {user_id} checked in at {check_in_time} "
                        f"(status: {checkin_status}, late: {late_minutes} min)"
                    )
                    return True

                except sqlite3.IntegrityError as e:
                    logger.warning(
                        f"Duplicate check-in attempt for user {user_id} on {today}. "
                        f"User already checked in today. Error: {e}"
                    )
                    return False

        except Exception as e:
            logger.error(f"Error recording check-in for user {user_id}: {e}")
            return False

    @staticmethod
    def check_out(
        user_id: int,
        latitude: float,
        longitude: float,
        check_out_time: Optional[datetime] = None
    ) -> bool:
        """
        Record a check-out.

        COMMIT 2: Added transaction handling for safer updates.
        """
        try:
            if check_out_time is None:
                check_out_time = Config.now()  # TIMEZONE FIX: Changed from datetime.now()

            today = check_out_time.date()

            with get_db() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT check_in_time FROM attendance
                    WHERE user_id = ? AND date = ?
                """, (user_id, today))

                row = cursor.fetchone()
                if not row:
                    logger.warning(f"No check-in found for user {user_id} on {today}")
                    return False

                check_in_time = datetime.fromisoformat(row[0])
                total_hours = (check_out_time - check_in_time).total_seconds() / 3600

                try:
                    cursor.execute("""
                        UPDATE attendance SET
                            check_out_time = ?,
                            check_out_latitude = ?,
                            check_out_longitude = ?,
                            total_hours = ?,
                            status = 'checked_out',
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ? AND date = ?
                    """, (check_out_time, latitude, longitude, total_hours, user_id, today))

                    if cursor.rowcount == 0:
                        logger.warning(f"Check-out update affected 0 rows for user {user_id}")
                        return False

                    logger.info(f"User {user_id} checked out at {check_out_time}, hours: {total_hours:.2f}")
                    return True

                except sqlite3.IntegrityError as e:
                    logger.error(f"Integrity error during check-out for user {user_id}: {e}")
                    return False

        except Exception as e:
            logger.error(f"Error recording check-out for user {user_id}: {e}")
            return False

    @staticmethod
    def get_today_status(user_id: int) -> Optional[Dict[str, Any]]:
        """Get today's attendance status for a user."""
        try:
            today = Config.today()  # TIMEZONE FIX: Changed from date.today()

            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM attendance
                    WHERE user_id = ? AND date = ?
                """, (user_id, today))

                row = cursor.fetchone()
                return dict(row) if row else None

        except Exception as e:
            logger.error(f"Error fetching today's status for user {user_id}: {e}")
            return None

    @staticmethod
    def get_user_history(user_id: int, limit: int = 7) -> List[Dict[str, Any]]:
        """Get attendance history for a user."""
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM attendance
                    WHERE user_id = ?
                    ORDER BY date DESC
                    LIMIT ?
                """, (user_id, limit))

                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Error fetching history for user {user_id}: {e}")
            return []

    @staticmethod
    def get_daily_report(target_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """Get attendance report for a specific date."""
        try:
            if target_date is None:
                target_date = Config.today()  # TIMEZONE FIX: Changed from date.today()

            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT
                        a.*,
                        t.username,
                        t.first_name,
                        t.last_name
                    FROM attendance a
                    JOIN teachers t ON a.user_id = t.user_id
                    WHERE a.date = ?
                    ORDER BY a.check_in_time
                """, (target_date,))

                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Error fetching daily report for {target_date}: {e}")
            return []


class AdminLog:
    """Admin log model for auditing."""

    @staticmethod
    def log_action(
        admin_user_id: int,
        action: str,
        target_user_id: Optional[int] = None,
        details: Optional[str] = None
    ) -> bool:
        """Log an admin action."""
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO admin_logs (
                        admin_user_id, action, target_user_id, details
                    ) VALUES (?, ?, ?, ?)
                """, (admin_user_id, action, target_user_id, details))

                logger.info(f"Admin action logged: {admin_user_id} - {action}")
                return True

        except Exception as e:
            logger.error(f"Error logging admin action: {e}")
            return False

    @staticmethod
    def get_recent_logs(limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent admin logs."""
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT
                        al.*,
                        t.username,
                        t.first_name,
                        t.last_name
                    FROM admin_logs al
                    JOIN teachers t ON al.admin_user_id = t.user_id
                    ORDER BY al.timestamp DESC
                    LIMIT ?
                """, (limit,))

                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Error fetching admin logs: {e}")
            return []
