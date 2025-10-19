"""
Database connection management with context manager.
Provides safe SQLite operations with automatic cleanup.

PHASE 2 UPDATE: Added notification tracking (schedule moved to Config).
"""
import sqlite3
import logging
from contextlib import contextmanager
from typing import Generator

from config import Config

logger = logging.getLogger(__name__)


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for database connections.
    Ensures connections are properly closed and committed.

    Yields:
        sqlite3.Connection: Database connection

    Example:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM teachers")
    """
    conn = None
    try:
        conn = sqlite3.connect(Config.DB_PATH)
        conn.row_factory = sqlite3.Row  # Access columns by name
        logger.debug(f"Database connection opened: {Config.DB_PATH}")
        yield conn
        conn.commit()
        logger.debug("Database transaction committed")
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
            logger.error(f"Database error, transaction rolled back: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed")


def init_database() -> None:
    """
    Initialize database with required tables.
    Creates tables if they don't exist.
    Safe to call multiple times (idempotent).

    PHASE 2: Added notifications_log and updated teachers/attendance tables.
    """
    logger.info("Initializing database...")

    with get_db() as conn:
        cursor = conn.cursor()

        # ====================================================================
        # EXISTING TABLES (Phase 1)
        # ====================================================================

        # Teachers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT NOT NULL,
                last_name TEXT,
                phone_number TEXT,
                language TEXT DEFAULT 'uz',
                is_admin INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.debug("Teachers table created/verified")

        # Attendance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                check_in_time TIMESTAMP,
                check_in_latitude REAL,
                check_in_longitude REAL,
                check_out_time TIMESTAMP,
                check_out_latitude REAL,
                check_out_longitude REAL,
                total_hours REAL,
                status TEXT DEFAULT 'checked_in',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES teachers(user_id),
                UNIQUE(user_id, date)
            )
        """)
        logger.debug("Attendance table created/verified")

        # Admin logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                target_user_id INTEGER,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (admin_user_id) REFERENCES teachers(user_id)
            )
        """)
        logger.debug("Admin logs table created/verified")

        # ====================================================================
        # PHASE 2: NEW TABLE FOR NOTIFICATION TRACKING
        # ====================================================================

        # Notifications log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                notification_type TEXT NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                was_delivered INTEGER DEFAULT 1,
                error_message TEXT,
                FOREIGN KEY (user_id) REFERENCES teachers(user_id)
            )
        """)
        logger.debug("Notifications log table created/verified")

        # ====================================================================
        # PHASE 2: ALTER EXISTING TABLES (Add new columns)
        # ====================================================================

        # Add notification preferences to teachers table
        try:
            # Check if columns already exist
            cursor.execute("PRAGMA table_info(teachers)")
            columns = [column[1] for column in cursor.fetchall()]

            if 'notification_enabled' not in columns:
                cursor.execute("""
                    ALTER TABLE teachers
                    ADD COLUMN notification_enabled INTEGER DEFAULT 1
                """)
                logger.info("Added notification_enabled column to teachers table")

            if 'notification_time_before' not in columns:
                cursor.execute("""
                    ALTER TABLE teachers
                    ADD COLUMN notification_time_before INTEGER DEFAULT 15
                """)
                logger.info("Added notification_time_before column to teachers table")

        except sqlite3.Error as e:
            logger.error(f"Error adding columns to teachers table: {e}")

        # Add lateness tracking to attendance table
        try:
            cursor.execute("PRAGMA table_info(attendance)")
            columns = [column[1] for column in cursor.fetchall()]

            if 'late_minutes' not in columns:
                cursor.execute("""
                    ALTER TABLE attendance
                    ADD COLUMN late_minutes INTEGER DEFAULT 0
                """)
                logger.info("Added late_minutes column to attendance table")

            if 'checkin_status' not in columns:
                cursor.execute("""
                    ALTER TABLE attendance
                    ADD COLUMN checkin_status TEXT DEFAULT 'on_time'
                """)
                logger.info("Added checkin_status column to attendance table")

        except sqlite3.Error as e:
            logger.error(f"Error adding columns to attendance table: {e}")

        # ====================================================================
        # CREATE INDICES FOR PERFORMANCE
        # ====================================================================

        # Existing indices
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_attendance_user_date
            ON attendance(user_id, date)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_attendance_date
            ON attendance(date)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_teachers_language
            ON teachers(language)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_admin_logs_timestamp
            ON admin_logs(timestamp)
        """)

        # PHASE 2: New indices
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notifications_user_id
            ON notifications_log(user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notifications_sent_at
            ON notifications_log(sent_at)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_notifications_type
            ON notifications_log(notification_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_attendance_checkin_status
            ON attendance(checkin_status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_teachers_notifications
            ON teachers(notification_enabled)
        """)

        logger.debug("Database indices created/verified")

    logger.info("Database initialization complete")


def get_db_stats() -> dict:
    """
    Get database statistics for monitoring.

    PHASE 2: Added notifications stats.

    Returns:
        dict: Database statistics
    """
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM teachers")
        teacher_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM attendance")
        attendance_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM admin_logs")
        log_count = cursor.fetchone()[0]

        # PHASE 2: Notification stats
        cursor.execute("SELECT COUNT(*) FROM notifications_log")
        notifications_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM notifications_log
            WHERE sent_at >= datetime('now', '-7 days')
        """)
        notifications_week = cursor.fetchone()[0]

        # Teachers with notifications enabled
        cursor.execute("""
            SELECT COUNT(*) FROM teachers
            WHERE notification_enabled = 1 AND is_active = 1
        """)
        notifications_enabled_count = cursor.fetchone()[0]

        return {
            'teachers': teacher_count,
            'attendance_records': attendance_count,
            'admin_logs': log_count,
            'notifications_total': notifications_count,
            'notifications_this_week': notifications_week,
            'notifications_enabled_users': notifications_enabled_count
        }
