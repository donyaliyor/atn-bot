"""
Database connection management with context manager.
Provides safe SQLite operations with automatic cleanup.
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
    """
    logger.info("Initializing database...")

    with get_db() as conn:
        cursor = conn.cursor()

        # Teachers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT NOT NULL,
                last_name TEXT,
                phone_number TEXT,
                language TEXT DEFAULT 'en',
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

        # Create indices for performance
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
        logger.debug("Database indices created/verified")

    logger.info("Database initialization complete")


def get_db_stats() -> dict:
    """
    Get database statistics for monitoring.

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

        return {
            'teachers': teacher_count,
            'attendance_records': attendance_count,
            'admin_logs': log_count
        }
