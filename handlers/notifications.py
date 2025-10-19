"""
Smart notification handlers for scheduled reminders.
Sends timely reminders based on work schedule configuration.

Notification Types:
- Morning Reminder: Sent before work starts
- Late Warning: Sent if user hasn't checked in after grace period
- Checkout Reminder: Sent before work ends
- Forgotten Checkout: Sent if user forgot to check out
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

    Sent at: WORK_START_TIME - MORNING_REMINDER_MINUTES_BEFORE
    Example: If work starts at 08:00 and reminder is 15 min before = 07:45

    Message: "Good morning! Don't forget to check in when you arrive at school."

    Args:
        context: Callback context from JobQueue
    """
    logger.info("=" * 60)
    logger.info("MORNING REMINDER JOB STARTED")
    logger.info("=" * 60)

    try:
        # Check if today is a working day
        if not WorkSchedule.is_working_day():
            logger.info("Today is not a working day, skipping morning reminder")
            return

        # Get all active teachers with notifications enabled
        teachers = Teacher.get_all_active()

        if not teachers:
            logger.warning("No active teachers found")
            return

        # Filter teachers who have notifications enabled
        notified_count = 0
        skipped_count = 0
        error_count = 0

        for teacher in teachers:
            user_id = teacher['user_id']

            # Check if notifications are enabled for this user
            if not teacher.get('notification_enabled', 1):
                logger.debug(f"User {user_id} has notifications disabled, skipping")
                skipped_count += 1
                continue

            # Check if user already checked in today
            status = Attendance.get_today_status(user_id)
            if status:
                logger.debug(f"User {user_id} already checked in, skipping reminder")
                skipped_count += 1
                continue

            # Send reminder
            try:
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

                # Log successful notification
                NotificationLog.log_notification(
                    user_id=user_id,
                    notification_type='morning_reminder',
                    was_delivered=True
                )

                notified_count += 1
                logger.info(f"Morning reminder sent to user {user_id}")

            except Exception as e:
                logger.error(f"Error sending morning reminder to user {user_id}: {e}")

                # Log failed notification
                NotificationLog.log_notification(
                    user_id=user_id,
                    notification_type='morning_reminder',
                    was_delivered=False,
                    error_message=str(e)
                )

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

    Sent at: WORK_START_TIME + LATE_WARNING_MINUTES_AFTER
    Example: If work starts at 08:00 and warning is 15 min after = 08:15

    Message: "You haven't checked in yet. Grace period ends soon!"

    Args:
        context: Callback context from JobQueue
    """
    logger.info("=" * 60)
    logger.info("LATE WARNING JOB STARTED")
    logger.info("=" * 60)

    try:
        # Check if today is a working day
        if not WorkSchedule.is_working_day():
            logger.info("Today is not a working day, skipping late warning")
            return

        # Get all active teachers
        teachers = Teacher.get_all_active()

        if not teachers:
            logger.warning("No active teachers found")
            return

        # Calculate grace period deadline
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

        notified_count = 0
        skipped_count = 0
        error_count = 0

        for teacher in teachers:
            user_id = teacher['user_id']

            # Check if notifications are enabled
            if not teacher.get('notification_enabled', 1):
                skipped_count += 1
                continue

            # Check if user has checked in today
            status = Attendance.get_today_status(user_id)
            if status:
                logger.debug(f"User {user_id} already checked in, skipping warning")
                skipped_count += 1
                continue

            # User hasn't checked in - send warning
            try:
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

                # Log notification
                NotificationLog.log_notification(
                    user_id=user_id,
                    notification_type='late_warning',
                    was_delivered=True
                )

                notified_count += 1
                logger.info(f"Late warning sent to user {user_id}")

            except Exception as e:
                logger.error(f"Error sending late warning to user {user_id}: {e}")

                NotificationLog.log_notification(
                    user_id=user_id,
                    notification_type='late_warning',
                    was_delivered=False,
                    error_message=str(e)
                )

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

    Sent at: WORK_END_TIME - CHECKOUT_REMINDER_MINUTES_BEFORE
    Example: If work ends at 17:00 and reminder is 15 min before = 16:45

    Message: "Work day is ending soon. Remember to check out before leaving!"

    Args:
        context: Callback context from JobQueue
    """
    logger.info("=" * 60)
    logger.info("CHECKOUT REMINDER JOB STARTED")
    logger.info("=" * 60)

    try:
        # Check if today is a working day
        if not WorkSchedule.is_working_day():
            logger.info("Today is not a working day, skipping checkout reminder")
            return

        # Get all active teachers
        teachers = Teacher.get_all_active()

        if not teachers:
            logger.warning("No active teachers found")
            return

        end_time = Config.WORK_END_TIME

        notified_count = 0
        skipped_count = 0
        error_count = 0

        for teacher in teachers:
            user_id = teacher['user_id']

            # Check if notifications are enabled
            if not teacher.get('notification_enabled', 1):
                skipped_count += 1
                continue

            # Check if user is checked in but not checked out
            status = Attendance.get_today_status(user_id)

            if not status:
                # User never checked in
                logger.debug(f"User {user_id} never checked in, skipping checkout reminder")
                skipped_count += 1
                continue

            if status.get('check_out_time'):
                # User already checked out
                logger.debug(f"User {user_id} already checked out, skipping reminder")
                skipped_count += 1
                continue

            # User is checked in but not checked out - send reminder
            try:
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

                # Log notification
                NotificationLog.log_notification(
                    user_id=user_id,
                    notification_type='checkout_reminder',
                    was_delivered=True
                )

                notified_count += 1
                logger.info(f"Checkout reminder sent to user {user_id}")

            except Exception as e:
                logger.error(f"Error sending checkout reminder to user {user_id}: {e}")

                NotificationLog.log_notification(
                    user_id=user_id,
                    notification_type='checkout_reminder',
                    was_delivered=False,
                    error_message=str(e)
                )

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

    Sent at: WORK_END_TIME + FORGOTTEN_CHECKOUT_MINUTES_AFTER
    Example: If work ends at 17:00 and alert is 30 min after = 17:30

    Message: "You forgot to check out! Please check out now to record your work hours."

    Args:
        context: Callback context from JobQueue
    """
    logger.info("=" * 60)
    logger.info("FORGOTTEN CHECKOUT ALERT JOB STARTED")
    logger.info("=" * 60)

    try:
        # Check if today is a working day
        if not WorkSchedule.is_working_day():
            logger.info("Today is not a working day, skipping forgotten checkout alert")
            return

        # Get all active teachers
        teachers = Teacher.get_all_active()

        if not teachers:
            logger.warning("No active teachers found")
            return

        notified_count = 0
        skipped_count = 0
        error_count = 0

        for teacher in teachers:
            user_id = teacher['user_id']

            # Check if notifications are enabled
            if not teacher.get('notification_enabled', 1):
                skipped_count += 1
                continue

            # Check if user is still checked in (forgot to check out)
            status = Attendance.get_today_status(user_id)

            if not status:
                # User never checked in
                logger.debug(f"User {user_id} never checked in, skipping forgotten checkout alert")
                skipped_count += 1
                continue

            if status.get('check_out_time'):
                # User already checked out (good!)
                logger.debug(f"User {user_id} already checked out, skipping alert")
                skipped_count += 1
                continue

            # User forgot to check out - send urgent alert
            try:
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

                # Log notification
                NotificationLog.log_notification(
                    user_id=user_id,
                    notification_type='forgotten_checkout',
                    was_delivered=True
                )

                notified_count += 1
                logger.info(f"Forgotten checkout alert sent to user {user_id}")

            except Exception as e:
                logger.error(f"Error sending forgotten checkout alert to user {user_id}: {e}")

                NotificationLog.log_notification(
                    user_id=user_id,
                    notification_type='forgotten_checkout',
                    was_delivered=False,
                    error_message=str(e)
                )

                error_count += 1

        logger.info("=" * 60)
        logger.info("FORGOTTEN CHECKOUT ALERT JOB COMPLETED")
        logger.info(f"  - Notified: {notified_count}")
        logger.info(f"  - Skipped: {skipped_count}")
        logger.info(f"  - Errors: {error_count}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Fatal error in forgotten checkout alert job: {e}", exc_info=True)
