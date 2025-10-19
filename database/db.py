"""
Database connection management with context manager.
Provides safe SQLite operations with automatic cleanup.
"""
import sqlite3
import logging
from contextlib import contextmanager
from typing import Generator
from pathlib import Path

from config import Config

logger = logging.getLogger(__name__)


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connections with optimizations."""
    conn = None
    try:
        conn = sqlite3.connect(
            Config.DB_PATH,
            timeout=30.0,
            check_same_thread=False
        )
        conn.row_factory = sqlite3.Row

        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=-20000")
        conn.execute("PRAGMA temp_store=MEMORY")
        conn.execute("PRAGMA foreign_keys=ON")

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
    """Initialize database with required tables."""
    logger.info("Initializing database...")
    logger.info(f"Database location: {Config.DB_PATH}")

    db_path = Path(Config.DB_PATH)
    if not db_path.parent.exists():
        raise RuntimeError(f"Database directory does not exist: {db_path.parent}")

    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("PRAGMA journal_mode=WAL")
        result = cursor.fetchone()
        logger.info(f"Database journal mode: {result[0]}")

        if result[0].lower() != 'wal':
            logger.warning("Failed to enable WAL mode")

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

        try:
            cursor.execute("PRAGMA table_info(teachers)")
            columns = [column[1] for column in cursor.fetchall()]

            if 'notification_enabled' not in columns:
                cursor.execute("ALTER TABLE teachers ADD COLUMN notification_enabled INTEGER DEFAULT 1")
                logger.info("Added notification_enabled column")

            if 'notification_time_before' not in columns:
                cursor.execute("ALTER TABLE teachers ADD COLUMN notification_time_before INTEGER DEFAULT 15")
                logger.info("Added notification_time_before column")

        except sqlite3.Error as e:
            logger.error(f"Error adding columns to teachers: {e}")

        try:
            cursor.execute("PRAGMA table_info(attendance)")
            columns = [column[1] for column in cursor.fetchall()]

            if 'late_minutes' not in columns:
                cursor.execute("ALTER TABLE attendance ADD COLUMN late_minutes INTEGER DEFAULT 0")
                logger.info("Added late_minutes column")

            if 'checkin_status' not in columns:
                cursor.execute("ALTER TABLE attendance ADD COLUMN checkin_status TEXT DEFAULT 'on_time'")
                logger.info("Added checkin_status column")

        except sqlite3.Error as e:
            logger.error(f"Error adding columns to attendance: {e}")

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_user_date ON attendance(user_id, date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_teachers_language ON teachers(language)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_admin_logs_timestamp ON admin_logs(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications_log(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_sent_at ON notifications_log(sent_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications_log(notification_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_checkin_status ON attendance(checkin_status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_teachers_notifications ON teachers(notification_enabled)")

        logger.debug("Database indices created/verified")

        cursor.execute("PRAGMA integrity_check")
        integrity = cursor.fetchone()[0]
        if integrity != 'ok':
            logger.error(f"Database integrity check failed: {integrity}")
            raise RuntimeError("Database corrupted!")

        logger.info("Database integrity check passed")

    logger.info("Database initialization complete")


def get_db_stats() -> dict:
    """Get database statistics for monitoring."""
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM teachers")
        teacher_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM attendance")
        attendance_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM admin_logs")
        log_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM notifications_log")
        notifications_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM notifications_log WHERE sent_at >= datetime('now', '-7 days')")
        notifications_week = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM teachers WHERE notification_enabled = 1 AND is_active = 1")
        notifications_enabled_count = cursor.fetchone()[0]

        cursor.execute("PRAGMA journal_mode")
        journal_mode = cursor.fetchone()[0]

        db_path = Path(Config.DB_PATH)
        db_size_mb = db_path.stat().st_size / (1024 * 1024) if db_path.exists() else 0

        return {
            'teachers': teacher_count,
            'attendance_records': attendance_count,
            'admin_logs': log_count,
            'notifications_total': notifications_count,
            'notifications_this_week': notifications_week,
            'notifications_enabled_users': notifications_enabled_count,
            'journal_mode': journal_mode,
            'database_size_mb': round(db_size_mb, 2),
            'database_path': str(Config.DB_PATH)
        }


def checkpoint_wal():
    """Manually checkpoint the WAL file."""
    try:
        with get_db() as conn:
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        logger.info("WAL checkpoint completed")
    except Exception as e:
        logger.error(f"WAL checkpoint failed: {e}")


def vacuum_database():
    """Vacuum database to reclaim space."""
    try:
        with get_db() as conn:
            conn.execute("VACUUM")
        logger.info("Database vacuum completed")
    except Exception as e:
        logger.error(f"Database vacuum failed: {e}")
