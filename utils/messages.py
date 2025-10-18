"""
Message formatting utilities.
Provides consistent message formatting across the bot.
"""
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


def format_check_in_success(check_in_time: datetime, distance: float) -> str:
    """
    Format successful check-in message.

    Args:
        check_in_time: Time of check-in
        distance: Distance from school in meters

    Returns:
        str: Formatted message
    """
    return (
        f"✅ **Check-In Successful!**\n\n"
        f"🕐 Time: {check_in_time.strftime('%H:%M:%S')}\n"
        f"📍 Distance: {distance:.1f}m from school\n"
        f"📅 Date: {check_in_time.strftime('%Y-%m-%d')}\n\n"
        f"Have a great day! 😊\n"
        f"Don't forget to check out when you leave."
    )


def format_check_out_success(
    check_out_time: datetime,
    check_in_time: datetime,
    total_hours: float,
    distance: float
) -> str:
    """
    Format successful check-out message.

    Args:
        check_out_time: Time of check-out
        check_in_time: Time of check-in
        total_hours: Total hours worked
        distance: Distance from school in meters

    Returns:
        str: Formatted message
    """
    return (
        f"🚪 **Check-Out Successful!**\n\n"
        f"🕐 Check-out: {check_out_time.strftime('%H:%M:%S')}\n"
        f"🕐 Check-in: {check_in_time.strftime('%H:%M:%S')}\n"
        f"⏱ Total hours: {total_hours:.2f}h\n"
        f"📍 Distance: {distance:.1f}m from school\n\n"
        f"Great work today! 👏"
    )


def format_distance_error(distance: float, required_radius: int) -> str:
    """
    Format distance error message.

    Args:
        distance: Actual distance in meters
        required_radius: Required radius in meters

    Returns:
        str: Formatted error message
    """
    return (
        f"❌ **Too Far From School**\n\n"
        f"📍 Your distance: {distance:.1f}m\n"
        f"📏 Required: Within {required_radius}m\n"
        f"🚶 You need to be {distance - required_radius:.1f}m closer\n\n"
        f"Please move closer to the school and try again."
    )


def format_already_checked_in(check_in_time: datetime) -> str:
    """
    Format already checked-in error message.

    Args:
        check_in_time: Time of original check-in

    Returns:
        str: Formatted error message
    """
    return (
        f"⚠️ **Already Checked In**\n\n"
        f"You already checked in today at {check_in_time.strftime('%H:%M:%S')}.\n\n"
        f"Use /checkout when you're ready to leave."
    )


def format_not_checked_in() -> str:
    """
    Format not-checked-in error message.

    Returns:
        str: Formatted error message
    """
    return (
        f"⚠️ **Not Checked In**\n\n"
        f"You haven't checked in yet today.\n\n"
        f"Use /checkin first to mark your arrival."
    )


def format_already_checked_out() -> str:
    """
    Format already checked-out error message.

    Returns:
        str: Formatted error message
    """
    return (
        f"⚠️ **Already Checked Out**\n\n"
        f"You have already completed your attendance for today.\n\n"
        f"See you tomorrow! 👋"
    )
