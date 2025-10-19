"""
Attendance handlers for check-in and check-out operations.
Now with multi-language support and late detection!

PHASE 2: Added late arrival detection with grace period.
"""
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from config import Config
from database.models import Attendance, Teacher
from database.schedule_models import WorkSchedule
from utils.location import is_within_radius, validate_coordinates, format_coordinates
from utils.decorators import weekday_only, registered_user_only
from utils.keyboards import get_location_keyboard, remove_keyboard
from locales import get_message

logger = logging.getLogger(__name__)


@weekday_only
@registered_user_only
async def checkin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /checkin command.
    Initiates check-in process by requesting location.

    Args:
        update: Telegram update object
        context: Callback context
    """
    user = update.effective_user
    logger.info(f"User {user.id} initiated check-in")

    # Get user's language
    lang = Teacher.get_language(user.id)

    # Check if already checked in
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

    # Request location
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

    # Set state for location handler
    context.user_data['awaiting_checkin_location'] = True


@weekday_only
@registered_user_only
async def checkout_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /checkout command.
    Initiates check-out process by requesting location.

    Args:
        update: Telegram update object
        context: Callback context
    """
    user = update.effective_user
    logger.info(f"User {user.id} initiated check-out")

    # Get user's language
    lang = Teacher.get_language(user.id)

    # Check if checked in
    status = Attendance.get_today_status(user.id)
    if not status:
        message = get_message(lang, 'not_checked_in')
        await update.message.reply_text(message, parse_mode='Markdown')
        return

    if status['check_out_time']:
        message = get_message(lang, 'already_checked_out')
        await update.message.reply_text(message, parse_mode='Markdown')
        return

    # Request location
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

    # Set state for location handler
    context.user_data['awaiting_checkout_location'] = True


async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle location messages from users.
    Processes check-in or check-out based on context.

    Args:
        update: Telegram update object
        context: Callback context
    """
    user = update.effective_user
    location = update.message.location

    if not location:
        logger.warning(f"User {user.id} sent message without location")
        return

    # Get user's language
    lang = Teacher.get_language(user.id)

    user_lat = location.latitude
    user_lon = location.longitude

    logger.info(f"User {user.id} shared location: ({user_lat:.6f}, {user_lon:.6f})")

    # Validate coordinates
    if not validate_coordinates(user_lat, user_lon):
        message = get_message(lang, 'error_invalid_location')
        await update.message.reply_text(message, reply_markup=remove_keyboard())
        return

    # Check if within radius
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

    # Process check-in
    if context.user_data.get('awaiting_checkin_location'):
        await process_checkin(update, context, user_lat, user_lon, distance, lang)
        context.user_data['awaiting_checkin_location'] = False

    # Process check-out
    elif context.user_data.get('awaiting_checkout_location'):
        await process_checkout(update, context, user_lat, user_lon, distance, lang)
        context.user_data['awaiting_checkout_location'] = False

    else:
        # Unsolicited location - inform user
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
    """
    Process check-in with validated location.

    PHASE 2: Now detects late arrivals based on work schedule.

    Args:
        update: Telegram update object
        context: Callback context
        latitude: User's latitude
        longitude: User's longitude
        distance: Distance from school
        lang: User's language
    """
    user = update.effective_user
    check_in_time = datetime.now()

    # PHASE 2: Detect late arrival
    is_late, minutes_late = WorkSchedule.is_late_checkin(check_in_time)
    checkin_status = WorkSchedule.get_checkin_status(check_in_time)

    logger.info(
        f"Check-in for user {user.id}: "
        f"{'LATE' if is_late else 'ON TIME'} "
        f"({minutes_late} minutes late)" if is_late else "(on time)"
    )

    # Record check-in with lateness info
    success = Attendance.check_in(
        user.id,
        latitude,
        longitude,
        check_in_time,
        late_minutes=minutes_late,
        checkin_status=checkin_status
    )

    if success:
        # Choose message based on whether user is late
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

        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=remove_keyboard()
        )

        logger.info(
            f"User {user.id} checked in successfully at {check_in_time} "
            f"(status: {checkin_status}, late: {minutes_late} min)"
        )
    else:
        message = get_message(lang, 'error_checkin_failed')
        await update.message.reply_text(message, reply_markup=remove_keyboard())
        logger.error(f"Failed to record check-in for user {user.id}")


async def process_checkout(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    latitude: float,
    longitude: float,
    distance: float,
    lang: str
) -> None:
    """
    Process check-out with validated location.

    Args:
        update: Telegram update object
        context: Callback context
        latitude: User's latitude
        longitude: User's longitude
        distance: Distance from school
        lang: User's language
    """
    user = update.effective_user
    check_out_time = datetime.now()

    # Get today's status to get check-in time
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

    # Record check-out
    success = Attendance.check_out(user.id, latitude, longitude, check_out_time)

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
        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=remove_keyboard()
        )
        logger.info(f"User {user.id} checked out successfully at {check_out_time}, hours: {total_hours:.2f}")
    else:
        message = get_message(lang, 'error_checkout_failed')
        await update.message.reply_text(message, reply_markup=remove_keyboard())
        logger.error(f"Failed to record check-out for user {user.id}")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /cancel command.
    Cancels any ongoing operation.

    Args:
        update: Telegram update object
        context: Callback context
    """
    # Get user's language
    lang = Teacher.get_language(update.effective_user.id)

    # Clear any awaiting states
    context.user_data.pop('awaiting_checkin_location', None)
    context.user_data.pop('awaiting_checkout_location', None)

    message = get_message(lang, 'operation_cancelled')
    await update.message.reply_text(message, reply_markup=remove_keyboard())
    logger.info(f"User {update.effective_user.id} cancelled operation")
