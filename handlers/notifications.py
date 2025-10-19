"""
Smart notification handlers for scheduled reminders.
Sends timely reminders based on work schedule configuration.


"""
import logging
from datetime import datetime, date
from typing import List, Dict, Any
from telegram.ext import ContextTypes

from config import Config
from database.models import Teacher, Attendance
from database.schedule_models import NotificationLog, WorkSchedule
from locales import get_message

logger = logging.getLogger(__name__)


async def send_morning_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send morning check-in reminder to all active users with notifications enabled.

    COMMIT 2: Now includes error handling for each user individually.
    """
    logger.info("=" * 60)
    logger.info("MORNING REMINDER JOB STARTED")
    logger.info("=" * 60)

    notified_count = 0
    skipped_count = 0
    error_count = 0

    try:
        if not WorkSchedule.is_working_day():
            logger.info("Today is not a working day, skipping morning reminder")
            return

        teachers = Teacher.get_all_active()

        if not teachers:
            logger.warning("No active teachers found")
            return

        for teacher in teachers:
            user_id = teacher['user_id']

            try:
                if not teacher.get('notification_enabled', 1):
                    logger.debug(f"User {user_id} has notifications disabled, skipping")
                    skipped_count += 1
                    continue

                status = Attendance.get_today_status(user_id)
                if status:
                    logger.debug(f"User {user_id} already checked in, skipping reminder")
                    skipped_count += 1
                    continue

                lang = teacher.get('language', Config.DEFAULT_LANGUAGE)
                start_time = Config.WORK_START_TIME

                message = get_message(
                    lang,
                    'notif_morning_reminder',
                    start_time=start_time
                )

                await context.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode='Markdown'
                )

                NotificationLog.log_notification(
                    user_id=user_id,
                    notification_type='morning_reminder',
                    was_delivered=True
                )

                notified_count += 1
                logger.info(f"Morning reminder sent to user {user_id}")

            except Exception as e:
                logger.error(f"Error sending morning reminder to user {user_id}: {e}")

                try:
                    NotificationLog.log_notification(
                        user_id=user_id,
                        notification_type='morning_reminder',
                        was_delivered=False,
                        error_message=str(e)
                    )
                except Exception as log_error:
                    logger.error(f"Failed to log notification error: {log_error}")

                error_count += 1

        logger.info("=" * 60)
        logger.info("MORNING REMINDER JOB COMPLETED")
        logger.info(f"  - Notified: {notified_count}")
        logger.info(f"  - Skipped: {skipped_count}")
        logger.info(f"  - Errors: {error_count}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Fatal error in morning reminder job: {e}", exc_info=True)


async def send_late_warning(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send late check-in warning to users who haven't checked in yet.

    COMMIT 2: Now includes error handling for each user individually.
    """
    logger.info("=" * 60)
    logger.info("LATE WARNING JOB STARTED")
    logger.info("=" * 60)

    notified_count = 0
    skipped_count = 0
    error_count = 0

    try:
        if not WorkSchedule.is_working_day():
            logger.info("Today is not a working day, skipping late warning")
            return

        teachers = Teacher.get_all_active()

        if not teachers:
            logger.warning("No active teachers found")
            return

        start_time = Config.get_work_start_time()
        grace_period = Config.GRACE_PERIOD_MINUTES

        deadline = datetime.now().replace(
            hour=start_time.hour,
            minute=start_time.minute,
            second=0,
            microsecond=0
        )
        deadline_str = deadline.strftime('%H:%M')
        grace_deadline_str = (deadline.replace(
            minute=deadline.minute + grace_period
        )).strftime('%H:%M')

        for teacher in teachers:
            user_id = teacher['user_id']

            try:
                if not teacher.get('notification_enabled', 1):
                    skipped_count += 1
                    continue

                status = Attendance.get_today_status(user_id)
                if status:
                    logger.debug(f"User {user_id} already checked in, skipping warning")
                    skipped_count += 1
                    continue

                lang = teacher.get('language', Config.DEFAULT_LANGUAGE)

                message = get_message(
                    lang,
                    'notif_late_warning',
                    deadline=grace_deadline_str
                )

                await context.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode='Markdown'
                )

                NotificationLog.log_notification(
                    user_id=user_id,
                    notification_type='late_warning',
                    was_delivered=True
                )

                notified_count += 1
                logger.info(f"Late warning sent to user {user_id}")

            except Exception as e:
                logger.error(f"Error sending late warning to user {user_id}: {e}")

                try:
                    NotificationLog.log_notification(
                        user_id=user_id,
                        notification_type='late_warning',
                        was_delivered=False,
                        error_message=str(e)
                    )
                except Exception as log_error:
                    logger.error(f"Failed to log notification error: {log_error}")

                error_count += 1

        logger.info("=" * 60)
        logger.info("LATE WARNING JOB COMPLETED")
        logger.info(f"  - Notified: {notified_count}")
        logger.info(f"  - Skipped: {skipped_count}")
        logger.info(f"  - Errors: {error_count}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Fatal error in late warning job: {e}", exc_info=True)


async def send_checkout_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send checkout reminder to users who are still checked in.

    COMMIT 2: Now includes error handling for each user individually.
    """
    logger.info("=" * 60)
    logger.info("CHECKOUT REMINDER JOB STARTED")
    logger.info("=" * 60)

    notified_count = 0
    skipped_count = 0
    error_count = 0

    try:
        if not WorkSchedule.is_working_day():
            logger.info("Today is not a working day, skipping checkout reminder")
            return

        teachers = Teacher.get_all_active()

        if not teachers:
            logger.warning("No active teachers found")
            return

        end_time = Config.WORK_END_TIME

        for teacher in teachers:
            user_id = teacher['user_id']

            try:
                if not teacher.get('notification_enabled', 1):
                    skipped_count += 1
                    continue

                status = Attendance.get_today_status(user_id)

                if not status:
                    logger.debug(f"User {user_id} never checked in, skipping checkout reminder")
                    skipped_count += 1
                    continue

                if status.get('check_out_time'):
                    logger.debug(f"User {user_id} already checked out, skipping reminder")
                    skipped_count += 1
                    continue

                lang = teacher.get('language', Config.DEFAULT_LANGUAGE)

                message = get_message(
                    lang,
                    'notif_checkout_reminder',
                    end_time=end_time
                )

                await context.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode='Markdown'
                )

                NotificationLog.log_notification(
                    user_id=user_id,
                    notification_type='checkout_reminder',
                    was_delivered=True
                )

                notified_count += 1
                logger.info(f"Checkout reminder sent to user {user_id}")

            except Exception as e:
                logger.error(f"Error sending checkout reminder to user {user_id}: {e}")

                try:
                    NotificationLog.log_notification(
                        user_id=user_id,
                        notification_type='checkout_reminder',
                        was_delivered=False,
                        error_message=str(e)
                    )
                except Exception as log_error:
                    logger.error(f"Failed to log notification error: {log_error}")

                error_count += 1

        logger.info("=" * 60)
        logger.info("CHECKOUT REMINDER JOB COMPLETED")
        logger.info(f"  - Notified: {notified_count}")
        logger.info(f"  - Skipped: {skipped_count}")
        logger.info(f"  - Errors: {error_count}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Fatal error in checkout reminder job: {e}", exc_info=True)


async def send_forgotten_checkout(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send urgent alert to users who forgot to check out.

    COMMIT 2: Now includes error handling for each user individually.
    """
    logger.info("=" * 60)
    logger.info("FORGOTTEN CHECKOUT ALERT JOB STARTED")
    logger.info("=" * 60)

    notified_count = 0
    skipped_count = 0
    error_count = 0

    try:
        if not WorkSchedule.is_working_day():
            logger.info("Today is not a working day, skipping forgotten checkout alert")
            return

        teachers = Teacher.get_all_active()

        if not teachers:
            logger.warning("No active teachers found")
            return

        for teacher in teachers:
            user_id = teacher['user_id']

            try:
                if not teacher.get('notification_enabled', 1):
                    skipped_count += 1
                    continue

                status = Attendance.get_today_status(user_id)

                if not status:
                    logger.debug(f"User {user_id} never checked in, skipping forgotten checkout alert")
                    skipped_count += 1
                    continue

                if status.get('check_out_time'):
                    logger.debug(f"User {user_id} already checked out, skipping alert")
                    skipped_count += 1
                    continue

                lang = teacher.get('language', Config.DEFAULT_LANGUAGE)

                message = get_message(
                    lang,
                    'notif_forgotten_checkout'
                )

                await context.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode='Markdown'
                )

                NotificationLog.log_notification(
                    user_id=user_id,
                    notification_type='forgotten_checkout',
                    was_delivered=True
                )

                notified_count += 1
                logger.info(f"Forgotten checkout alert sent to user {user_id}")

            except Exception as e:
                logger.error(f"Error sending forgotten checkout alert to user {user_id}: {e}")

                try:
                    NotificationLog.log_notification(
                        user_id=user_id,
                        notification_type='forgotten_checkout',
                        was_delivered=False,
                        error_message=str(e)
                    )
                except Exception as log_error:
                    logger.error(f"Failed to log notification error: {log_error}")

                error_count += 1

        logger.info("=" * 60)
        logger.info("FORGOTTEN CHECKOUT ALERT JOB COMPLETED")
        logger.info(f"  - Notified: {notified_count}")
        logger.info(f"  - Skipped: {skipped_count}")
        logger.info(f"  - Errors: {error_count}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Fatal error in forgotten checkout alert job: {e}", exc_info=True)
