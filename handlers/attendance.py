"""
Attendance handlers for check-in and check-out operations.
Now with multi-language support and late detection!

FIX: Comprehensive error handling added to ALL functions
FIX: Detailed logging at every step of location processing
FIX: Users ALWAYS get a response, even on errors
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
    COMMIT 3: Enhanced error handling with detailed logging.
    """
    user = update.effective_user
    logger.info(f"User {user.id} initiated check-in")

    try:
        lang = Teacher.get_language(user.id)
        logger.debug(f"User {user.id} language: {lang}")

        status = Attendance.get_today_status(user.id)

        if status:
            logger.info(f"User {user.id} already has attendance record for today")
            if status['check_out_time']:
                message = get_message(lang, 'already_checked_out')
                logger.debug(f"User {user.id} already checked out today")
            else:
                check_in_time = datetime.fromisoformat(status['check_in_time'])
                message = get_message(
                    lang,
                    'already_checked_in',
                    time=check_in_time.strftime('%H:%M:%S')
                )
                logger.debug(f"User {user.id} already checked in at {check_in_time}")

            await update.message.reply_text(message, parse_mode='Markdown')
            return

        logger.debug(f"User {user.id} has no attendance record today, proceeding with check-in prompt")

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
        logger.info(f"Check-in prompt sent to user {user.id}, awaiting location")

    except Exception as e:
        logger.error(f"ERROR in checkin_command for user {user.id}: {e}", exc_info=True)

        # Try to send error message to user
        try:
            lang = Teacher.get_language(user.id) if user else 'en'
            error_message = get_message(lang, 'error_general')
            await update.message.reply_text(error_message)
            logger.info(f"Error message sent to user {user.id}")
        except Exception as send_error:
            logger.error(f"Failed to send error message to user {user.id}: {send_error}")


@rate_limit(seconds=2)
@weekday_only
@registered_user_only
async def checkout_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /checkout command.

    COMMIT 2: Added rate limiting (2 seconds) to prevent spam and race conditions.
    Rate limit decorator is applied FIRST (outermost) so it executes before other checks.
    COMMIT 3: Enhanced error handling with detailed logging.
    """
    user = update.effective_user
    logger.info(f"User {user.id} initiated check-out")

    try:
        lang = Teacher.get_language(user.id)
        logger.debug(f"User {user.id} language: {lang}")

        status = Attendance.get_today_status(user.id)

        if not status:
            logger.info(f"User {user.id} has not checked in yet today")
            message = get_message(lang, 'not_checked_in')
            await update.message.reply_text(message, parse_mode='Markdown')
            return

        if status['check_out_time']:
            logger.info(f"User {user.id} already checked out today")
            message = get_message(lang, 'already_checked_out')
            await update.message.reply_text(message, parse_mode='Markdown')
            return

        logger.debug(f"User {user.id} is checked in and ready to check out")

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
        logger.info(f"Check-out prompt sent to user {user.id}, awaiting location")

    except Exception as e:
        logger.error(f"ERROR in checkout_command for user {user.id}: {e}", exc_info=True)

        # Try to send error message to user
        try:
            lang = Teacher.get_language(user.id) if user else 'en'
            error_message = get_message(lang, 'error_general')
            await update.message.reply_text(error_message)
            logger.info(f"Error message sent to user {user.id}")
        except Exception as send_error:
            logger.error(f"Failed to send error message to user {user.id}: {send_error}")


async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle location messages from users.

    COMMIT 3: Comprehensive error handling with detailed logging at every step.
    Ensures user ALWAYS gets a response, even if errors occur.
    """
    user = update.effective_user

    logger.info("=" * 60)
    logger.info(f"LOCATION HANDLER STARTED for user {user.id}")
    logger.info("=" * 60)

    try:
        # Step 1: Validate location object exists
        location = update.message.location

        if not location:
            logger.warning(f"User {user.id} sent message without location data")
            return

        logger.info(f"✓ Location object received from user {user.id}")

        # Step 2: Get user language
        try:
            lang = Teacher.get_language(user.id)
            logger.debug(f"✓ User {user.id} language: {lang}")
        except Exception as lang_error:
            logger.error(f"Error getting language for user {user.id}: {lang_error}")
            lang = 'en'  # Fallback to English
            logger.info(f"Using fallback language: {lang}")

        # Step 3: Extract coordinates
        try:
            user_lat = location.latitude
            user_lon = location.longitude
            logger.info(f"✓ User {user.id} shared location: ({user_lat:.6f}, {user_lon:.6f})")
        except Exception as coord_error:
            logger.error(f"Error extracting coordinates for user {user.id}: {coord_error}", exc_info=True)
            message = get_message(lang, 'error_invalid_location')
            await update.message.reply_text(message, reply_markup=remove_keyboard())
            return

        # Step 4: Validate coordinates
        try:
            if not validate_coordinates(user_lat, user_lon):
                logger.warning(f"Invalid coordinates from user {user.id}: ({user_lat}, {user_lon})")
                message = get_message(lang, 'error_invalid_location')
                await update.message.reply_text(message, reply_markup=remove_keyboard())
                return
            logger.debug(f"✓ Coordinates validated for user {user.id}")
        except Exception as validate_error:
            logger.error(f"Error validating coordinates for user {user.id}: {validate_error}", exc_info=True)
            message = get_message(lang, 'error_location_validation')
            await update.message.reply_text(message, reply_markup=remove_keyboard())
            return

        # Step 5: Check distance from school
        try:
            logger.debug(f"Checking radius for user {user.id}")
            within_radius, distance = is_within_radius(user_lat, user_lon)
            logger.info(f"✓ Distance calculated for user {user.id}: {distance:.2f}m (within: {within_radius})")
        except Exception as radius_error:
            logger.error(f"Error checking radius for user {user.id}: {radius_error}", exc_info=True)
            message = get_message(lang, 'error_location_validation')
            await update.message.reply_text(message, reply_markup=remove_keyboard())
            return

        # Step 6: Check if within allowed radius
        if not within_radius:
            logger.warning(f"User {user.id} is too far: {distance:.2f}m (max: {Config.RADIUS_METERS}m)")
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

        logger.info(f"✓ User {user.id} is within allowed radius")

        # Step 7: Process check-in or check-out
        is_checkin = context.user_data.get('awaiting_checkin_location', False)
        is_checkout = context.user_data.get('awaiting_checkout_location', False)

        logger.debug(f"User {user.id} state - awaiting_checkin: {is_checkin}, awaiting_checkout: {is_checkout}")

        if is_checkin:
            logger.info(f"Processing CHECK-IN for user {user.id}")
            try:
                await process_checkin(update, context, user_lat, user_lon, distance, lang)
                context.user_data['awaiting_checkin_location'] = False
                logger.info(f"✓ Check-in processing completed for user {user.id}")
            except Exception as checkin_error:
                logger.error(f"ERROR during check-in processing for user {user.id}: {checkin_error}", exc_info=True)
                # Ensure we clear the flag even on error
                context.user_data['awaiting_checkin_location'] = False
                message = get_message(lang, 'error_checkin_failed')
                is_admin = Config.is_admin(user.id)
                menu_keyboard = get_admin_keyboard(lang) if is_admin else get_main_menu_keyboard(lang)
                await update.message.reply_text(message, reply_markup=menu_keyboard)

        elif is_checkout:
            logger.info(f"Processing CHECK-OUT for user {user.id}")
            try:
                await process_checkout(update, context, user_lat, user_lon, distance, lang)
                context.user_data['awaiting_checkout_location'] = False
                logger.info(f"✓ Check-out processing completed for user {user.id}")
            except Exception as checkout_error:
                logger.error(f"ERROR during check-out processing for user {user.id}: {checkout_error}", exc_info=True)
                # Ensure we clear the flag even on error
                context.user_data['awaiting_checkout_location'] = False
                message = get_message(lang, 'error_checkout_failed')
                is_admin = Config.is_admin(user.id)
                menu_keyboard = get_admin_keyboard(lang) if is_admin else get_main_menu_keyboard(lang)
                await update.message.reply_text(message, reply_markup=menu_keyboard)

        else:
            logger.warning(f"User {user.id} sent location without requesting check-in or check-out")
            await update.message.reply_text(
                "📍 Location received, but no action was requested.\n"
                "Use /checkin or /checkout first.",
                reply_markup=remove_keyboard()
            )

    except Exception as e:
        # Catch-all for any unexpected errors
        logger.error("=" * 60)
        logger.error(f"CRITICAL ERROR in handle_location for user {user.id if user else 'unknown'}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {e}", exc_info=True)
        logger.error("=" * 60)

        # Try to notify user
        try:
            if user:
                lang = Teacher.get_language(user.id) if user.id else 'en'
            else:
                lang = 'en'

            message = get_message(lang, 'error_general')

            if update and update.message:
                await update.message.reply_text(message)
                logger.info(f"Error notification sent to user {user.id if user else 'unknown'}")
        except Exception as notify_error:
            logger.error(f"Failed to send error notification: {notify_error}")

    finally:
        logger.info(f"LOCATION HANDLER COMPLETED for user {user.id if user else 'unknown'}")
        logger.info("=" * 60)


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

    COMMIT 3: Enhanced error handling with step-by-step logging.
    """
    user = update.effective_user

    logger.info(f"PROCESS_CHECKIN started for user {user.id}")

    try:
        # Step 1: Get current time
        try:
            check_in_time = Config.now()
            logger.debug(f"✓ Check-in time: {check_in_time}")
        except Exception as time_error:
            logger.error(f"Error getting current time for user {user.id}: {time_error}", exc_info=True)
            raise

        # Step 2: Check if late
        try:
            is_late, minutes_late = WorkSchedule.is_late_checkin(check_in_time)
            logger.debug(f"✓ Late check: is_late={is_late}, minutes_late={minutes_late}")
        except Exception as late_error:
            logger.error(f"Error checking late status for user {user.id}: {late_error}", exc_info=True)
            # Use defaults on error
            is_late = False
            minutes_late = 0
            logger.warning(f"Using default late values: is_late={is_late}, minutes_late={minutes_late}")

        # Step 3: Get check-in status
        try:
            checkin_status = WorkSchedule.get_checkin_status(check_in_time)
            logger.debug(f"✓ Check-in status: {checkin_status}")
        except Exception as status_error:
            logger.error(f"Error getting check-in status for user {user.id}: {status_error}", exc_info=True)
            checkin_status = 'late' if is_late else 'on_time'
            logger.warning(f"Using fallback status: {checkin_status}")

        logger.info(
            f"Check-in details for user {user.id}: "
            f"{'LATE' if is_late else 'ON TIME'} "
            f"({minutes_late} minutes late)" if is_late else "(on time)"
        )

        # Step 4: Record check-in in database
        try:
            logger.debug(f"Recording check-in to database for user {user.id}")
            success = Attendance.check_in(
                user.id,
                latitude,
                longitude,
                check_in_time,
                late_minutes=minutes_late,
                checkin_status=checkin_status
            )
            logger.debug(f"✓ Database operation result: {success}")
        except Exception as db_error:
            logger.error(f"Database error during check-in for user {user.id}: {db_error}", exc_info=True)
            success = False

        # Step 5: Get appropriate keyboard
        try:
            is_admin = Config.is_admin(user.id)
            menu_keyboard = get_admin_keyboard(lang) if is_admin else get_main_menu_keyboard(lang)
            logger.debug(f"✓ Keyboard prepared (admin: {is_admin})")
        except Exception as keyboard_error:
            logger.error(f"Error preparing keyboard for user {user.id}: {keyboard_error}")
            menu_keyboard = get_main_menu_keyboard(lang)  # Fallback to basic keyboard

        # Step 6: Send response to user
        if success:
            logger.info(f"✓ Check-in successful for user {user.id}")

            try:
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
                    reply_markup=menu_keyboard
                )
                logger.info(f"✓ Success message sent to user {user.id}")

            except Exception as msg_error:
                logger.error(f"Error sending success message to user {user.id}: {msg_error}", exc_info=True)
                # Try to send a basic success message
                try:
                    await update.message.reply_text(
                        "✅ Check-in successful!",
                        reply_markup=menu_keyboard
                    )
                except Exception as fallback_error:
                    logger.error(f"Failed to send fallback message: {fallback_error}")

            logger.info(
                f"PROCESS_CHECKIN completed successfully for user {user.id} at {check_in_time} "
                f"(status: {checkin_status}, late: {minutes_late} min)"
            )
        else:
            logger.error(f"✗ Check-in FAILED for user {user.id} - database operation returned False")

            try:
                message = get_message(lang, 'error_checkin_failed')
                await update.message.reply_text(message, reply_markup=menu_keyboard)
                logger.info(f"Error message sent to user {user.id}")
            except Exception as err_msg_error:
                logger.error(f"Failed to send error message to user {user.id}: {err_msg_error}")

    except Exception as e:
        logger.error(f"CRITICAL ERROR in process_checkin for user {user.id}: {e}", exc_info=True)

        # Always try to send an error message to the user
        try:
            message = get_message(lang, 'error_checkin_failed')
            is_admin = Config.is_admin(user.id)
            menu_keyboard = get_admin_keyboard(lang) if is_admin else get_main_menu_keyboard(lang)
            await update.message.reply_text(message, reply_markup=menu_keyboard)
        except Exception as final_error:
            logger.error(f"Failed to send final error message: {final_error}")

        # Re-raise to be caught by handle_location
        raise


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

    COMMIT 3: Enhanced error handling with step-by-step logging.
    """
    user = update.effective_user

    logger.info(f"PROCESS_CHECKOUT started for user {user.id}")

    try:
        # Step 1: Get current time
        try:
            check_out_time = Config.now()
            logger.debug(f"✓ Check-out time: {check_out_time}")
        except Exception as time_error:
            logger.error(f"Error getting current time for user {user.id}: {time_error}", exc_info=True)
            raise

        # Step 2: Get today's attendance status
        try:
            status = Attendance.get_today_status(user.id)
            logger.debug(f"✓ Today's status retrieved for user {user.id}")
        except Exception as status_error:
            logger.error(f"Error getting today's status for user {user.id}: {status_error}", exc_info=True)
            status = None

        if not status:
            logger.warning(f"User {user.id} attempted check-out without check-in")
            message = get_message(lang, 'not_checked_in')
            await update.message.reply_text(
                message,
                parse_mode='Markdown',
                reply_markup=remove_keyboard()
            )
            return

        # Step 3: Parse check-in time
        try:
            check_in_time = datetime.fromisoformat(status['check_in_time'])
            logger.debug(f"✓ Check-in time parsed: {check_in_time}")
        except Exception as parse_error:
            logger.error(f"Error parsing check-in time for user {user.id}: {parse_error}", exc_info=True)
            raise

        # Step 4: Record check-out in database
        try:
            logger.debug(f"Recording check-out to database for user {user.id}")
            success = Attendance.check_out(user.id, latitude, longitude, check_out_time)
            logger.debug(f"✓ Database operation result: {success}")
        except Exception as db_error:
            logger.error(f"Database error during check-out for user {user.id}: {db_error}", exc_info=True)
            success = False

        # Step 5: Get appropriate keyboard
        try:
            is_admin = Config.is_admin(user.id)
            menu_keyboard = get_admin_keyboard(lang) if is_admin else get_main_menu_keyboard(lang)
            logger.debug(f"✓ Keyboard prepared (admin: {is_admin})")
        except Exception as keyboard_error:
            logger.error(f"Error preparing keyboard for user {user.id}: {keyboard_error}")
            menu_keyboard = get_main_menu_keyboard(lang)  # Fallback

        # Step 6: Send response to user
        if success:
            logger.info(f"✓ Check-out successful for user {user.id}")

            try:
                total_hours = (check_out_time - check_in_time).total_seconds() / 3600
                logger.debug(f"✓ Total hours calculated: {total_hours:.2f}")

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
                    reply_markup=menu_keyboard
                )
                logger.info(f"✓ Success message sent to user {user.id}")

            except Exception as msg_error:
                logger.error(f"Error sending success message to user {user.id}: {msg_error}", exc_info=True)
                # Try to send a basic success message
                try:
                    await update.message.reply_text(
                        "✅ Check-out successful!",
                        reply_markup=menu_keyboard
                    )
                except Exception as fallback_error:
                    logger.error(f"Failed to send fallback message: {fallback_error}")

            logger.info(f"PROCESS_CHECKOUT completed successfully for user {user.id} at {check_out_time}")

        else:
            logger.error(f"✗ Check-out FAILED for user {user.id} - database operation returned False")

            try:
                message = get_message(lang, 'error_checkout_failed')
                await update.message.reply_text(message, reply_markup=menu_keyboard)
                logger.info(f"Error message sent to user {user.id}")
            except Exception as err_msg_error:
                logger.error(f"Failed to send error message to user {user.id}: {err_msg_error}")

    except Exception as e:
        logger.error(f"CRITICAL ERROR in process_checkout for user {user.id}: {e}", exc_info=True)

        # Always try to send an error message to the user
        try:
            message = get_message(lang, 'error_checkout_failed')
            is_admin = Config.is_admin(user.id)
            menu_keyboard = get_admin_keyboard(lang) if is_admin else get_main_menu_keyboard(lang)
            await update.message.reply_text(message, reply_markup=menu_keyboard)
        except Exception as final_error:
            logger.error(f"Failed to send final error message: {final_error}")

        # Re-raise to be caught by handle_location
        raise


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /cancel command.

    COMMIT 3: Enhanced error handling.
    """
    user = update.effective_user
    logger.info(f"User {user.id} initiated cancel operation")

    try:
        lang = Teacher.get_language(user.id)

        # Clear any pending location requests
        context.user_data.pop('awaiting_checkin_location', None)
        context.user_data.pop('awaiting_checkout_location', None)
        logger.debug(f"Cleared pending location requests for user {user.id}")

        # Get appropriate keyboard
        is_admin = Config.is_admin(user.id)
        menu_keyboard = get_admin_keyboard(lang) if is_admin else get_main_menu_keyboard(lang)

        message = get_message(lang, 'operation_cancelled')
        await update.message.reply_text(message, reply_markup=menu_keyboard)
        logger.info(f"Cancel operation completed for user {user.id}")

    except Exception as e:
        logger.error(f"Error in cancel_command for user {user.id}: {e}", exc_info=True)

        # Try to send a basic cancellation message
        try:
            await update.message.reply_text("Operation cancelled.")
        except Exception as send_error:
            logger.error(f"Failed to send cancellation message: {send_error}")
