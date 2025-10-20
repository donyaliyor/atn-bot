"""
Attendance handlers for check-in and check-out operations.
Now with multi-language support and late detection!

FIX: Restore main menu keyboard after check-in/check-out operations complete
"""
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from config import Config
from database.models import Attendance, Teacher
from database.schedule_models import WorkSchedule
from utils.location import is_within_radius, validate_coordinates, format_coordinates
from utils.decorators import weekday_only, registered_user_only, rate_limit
from utils.keyboards import get_location_keyboard, remove_keyboard, get_main_menu_keyboard, get_admin_keyboard
from locales import get_message

logger = logging.getLogger(__name__)


@rate_limit(seconds=2)
@weekday_only
@registered_user_only
async def checkin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /checkin command.

    COMMIT 2: Added rate limiting (2 seconds) to prevent spam and race conditions.
    Rate limit decorator is applied FIRST (outermost) so it executes before other checks.
    """
    user = update.effective_user
    logger.info(f"User {user.id} initiated check-in")

    lang = Teacher.get_language(user.id)

    status = Attendance.get_today_status(user.id)
    if status:
        if status['check_out_time']:
            message = get_message(lang, 'already_checked_out')
        else:
            check_in_time = datetime.fromisoformat(status['check_in_time'])
            message = get_message(
                lang,
                'already_checked_in',
                time=check_in_time.strftime('%H:%M:%S')
            )
        await update.message.reply_text(message, parse_mode='Markdown')
        return

    message = get_message(
        lang,
        'checkin_prompt',
        radius=Config.RADIUS_METERS,
        school_location=format_coordinates(Config.SCHOOL_LATITUDE, Config.SCHOOL_LONGITUDE)
    )

    await update.message.reply_text(
        message,
        parse_mode='Markdown',
        reply_markup=get_location_keyboard(lang)
    )

    context.user_data['awaiting_checkin_location'] = True


@rate_limit(seconds=2)
@weekday_only
@registered_user_only
async def checkout_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /checkout command.

    COMMIT 2: Added rate limiting (2 seconds) to prevent spam and race conditions.
    Rate limit decorator is applied FIRST (outermost) so it executes before other checks.
    """
    user = update.effective_user
    logger.info(f"User {user.id} initiated check-out")

    lang = Teacher.get_language(user.id)

    status = Attendance.get_today_status(user.id)
    if not status:
        message = get_message(lang, 'not_checked_in')
        await update.message.reply_text(message, parse_mode='Markdown')
        return

    if status['check_out_time']:
        message = get_message(lang, 'already_checked_out')
        await update.message.reply_text(message, parse_mode='Markdown')
        return

    message = get_message(
        lang,
        'checkout_prompt',
        radius=Config.RADIUS_METERS
    )

    await update.message.reply_text(
        message,
        parse_mode='Markdown',
        reply_markup=get_location_keyboard(lang)
    )

    context.user_data['awaiting_checkout_location'] = True


async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle location messages from users."""
    user = update.effective_user
    location = update.message.location

    if not location:
        logger.warning(f"User {user.id} sent message without location")
        return

    lang = Teacher.get_language(user.id)

    user_lat = location.latitude
    user_lon = location.longitude

    logger.info(f"User {user.id} shared location: ({user_lat:.6f}, {user_lon:.6f})")

    if not validate_coordinates(user_lat, user_lon):
        message = get_message(lang, 'error_invalid_location')
        await update.message.reply_text(message, reply_markup=remove_keyboard())
        return

    try:
        within_radius, distance = is_within_radius(user_lat, user_lon)
    except Exception as e:
        logger.error(f"Error checking radius for user {user.id}: {e}")
        message = get_message(lang, 'error_location_validation')
        await update.message.reply_text(message, reply_markup=remove_keyboard())
        return

    if not within_radius:
        message = get_message(
            lang,
            'error_distance',
            distance=f"{distance:.1f}",
            radius=Config.RADIUS_METERS,
            diff=f"{distance - Config.RADIUS_METERS:.1f}"
        )
        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=remove_keyboard()
        )
        return

    if context.user_data.get('awaiting_checkin_location'):
        await process_checkin(update, context, user_lat, user_lon, distance, lang)
        context.user_data['awaiting_checkin_location'] = False

    elif context.user_data.get('awaiting_checkout_location'):
        await process_checkout(update, context, user_lat, user_lon, distance, lang)
        context.user_data['awaiting_checkout_location'] = False

    else:
        await update.message.reply_text(
            "📍 Location received, but no action was requested.\n"
            "Use /checkin or /checkout first.",
            reply_markup=remove_keyboard()
        )


async def process_checkin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    latitude: float,
    longitude: float,
    distance: float,
    lang: str
) -> None:
    """Process check-in with validated location."""
    user = update.effective_user
    check_in_time = Config.now()  # TIMEZONE FIX: Changed from datetime.now()

    is_late, minutes_late = WorkSchedule.is_late_checkin(check_in_time)
    checkin_status = WorkSchedule.get_checkin_status(check_in_time)

    logger.info(
        f"Check-in for user {user.id}: "
        f"{'LATE' if is_late else 'ON TIME'} "
        f"({minutes_late} minutes late)" if is_late else "(on time)"
    )

    success = Attendance.check_in(
        user.id,
        latitude,
        longitude,
        check_in_time,
        late_minutes=minutes_late,
        checkin_status=checkin_status
    )

    # FIX: Get appropriate keyboard based on admin status
    is_admin = Config.is_admin(user.id)
    menu_keyboard = get_admin_keyboard(lang) if is_admin else get_main_menu_keyboard(lang)

    if success:
        if is_late:
            message = get_message(
                lang,
                'checkin_success_late',
                time=check_in_time.strftime('%H:%M:%S'),
                minutes_late=minutes_late,
                distance=f"{distance:.1f}",
                date=check_in_time.strftime('%Y-%m-%d')
            )
        else:
            message = get_message(
                lang,
                'checkin_success',
                time=check_in_time.strftime('%H:%M:%S'),
                distance=f"{distance:.1f}",
                date=check_in_time.strftime('%Y-%m-%d')
            )

        # FIX: Restore main menu keyboard instead of remove_keyboard()
        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=menu_keyboard
        )

        logger.info(
            f"User {user.id} checked in successfully at {check_in_time} "
            f"(status: {checkin_status}, late: {minutes_late} min)"
        )
    else:
        message = get_message(lang, 'error_checkin_failed')
        # FIX: Restore main menu keyboard even on error
        await update.message.reply_text(message, reply_markup=menu_keyboard)
        logger.error(f"Failed to record check-in for user {user.id}")


async def process_checkout(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    latitude: float,
    longitude: float,
    distance: float,
    lang: str
) -> None:
    """Process check-out with validated location."""
    user = update.effective_user
    check_out_time = Config.now()  # TIMEZONE FIX: Changed from datetime.now()

    status = Attendance.get_today_status(user.id)
    if not status:
        message = get_message(lang, 'not_checked_in')
        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=remove_keyboard()
        )
        return

    check_in_time = datetime.fromisoformat(status['check_in_time'])

    success = Attendance.check_out(user.id, latitude, longitude, check_out_time)

    # FIX: Get appropriate keyboard based on admin status
    is_admin = Config.is_admin(user.id)
    menu_keyboard = get_admin_keyboard(lang) if is_admin else get_main_menu_keyboard(lang)

    if success:
        total_hours = (check_out_time - check_in_time).total_seconds() / 3600
        message = get_message(
            lang,
            'checkout_success',
            checkout_time=check_out_time.strftime('%H:%M:%S'),
            checkin_time=check_in_time.strftime('%H:%M:%S'),
            hours=f"{total_hours:.2f}",
            distance=f"{distance:.1f}"
        )
        # FIX: Restore main menu keyboard instead of remove_keyboard()
        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=menu_keyboard
        )
        logger.info(f"User {user.id} checked out successfully at {check_out_time}, hours: {total_hours:.2f}")
    else:
        message = get_message(lang, 'error_checkout_failed')
        # FIX: Restore main menu keyboard even on error
        await update.message.reply_text(message, reply_markup=menu_keyboard)
        logger.error(f"Failed to record check-out for user {user.id}")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /cancel command."""
    user = update.effective_user
    lang = Teacher.get_language(user.id)

    context.user_data.pop('awaiting_checkin_location', None)
    context.user_data.pop('awaiting_checkout_location', None)

    # FIX: Restore main menu keyboard based on admin status
    is_admin = Config.is_admin(user.id)
    menu_keyboard = get_admin_keyboard(lang) if is_admin else get_main_menu_keyboard(lang)

    message = get_message(lang, 'operation_cancelled')
    await update.message.reply_text(message, reply_markup=menu_keyboard)
    logger.info(f"User {user.id} cancelled operation")
