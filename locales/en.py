"""
English language translations.
"""

MESSAGES = {
    # Welcome & Start
    'welcome': (
        "👋 Welcome {first_name}!\n\n"
        "🏫 **Attendance Bot**\n\n"
        "This bot helps teachers track their attendance with location verification.\n\n"
        "📍 You must be within {radius}m of school to check in/out.\n"
        "📅 Active on weekdays only.\n\n"
        "🆔 Your User ID: `{user_id}`\n"
        "👤 Registered as: {full_name}\n\n"
        "Use /help to see available commands."
    ),

    # Help
    'help_user': (
        "📚 **Available Commands:**\n\n"
        "**For All Users:**\n"
        "/start - Initialize bot and register\n"
        "/help - Show this help message\n"
        "/myid - Show your user ID\n"
        "/checkin - Check in with location ✅\n"
        "/checkout - Check out with location 🚪\n"
        "/status - View today's status\n"
        "/history - View attendance history\n"
        "/language - Change language 🌍\n"
        "/cancel - Cancel current operation\n"
    ),
    'help_admin': (
        "\n**Admin Commands:**\n"
        "/stats - View database statistics\n"
        "/admin - Access admin panel (coming soon)\n"
    ),

    # User Info
    'myid': (
        "👤 **Your Information:**\n\n"
        "🆔 User ID: `{user_id}`\n"
        "📝 Username: @{username}\n"
        "👔 Name: {full_name}\n"
        "🌍 Language: {language}\n"
        "🔑 Admin: {admin_status}\n\n"
        "💡 Save your User ID to add yourself as admin"
    ),

    # Check-in
    'checkin_prompt': (
        "📍 **Check-In Process**\n\n"
        "Please share your location to check in.\n\n"
        "⚠️ You must be within {radius}m of school:\n"
        "📍 {school_location}\n\n"
        "Tap the button below to share your location."
    ),
    'checkin_success': (
        "✅ **Check-In Successful!**\n\n"
        "🕐 Time: {time}\n"
        "📍 Distance: {distance}m from school\n"
        "📅 Date: {date}\n\n"
        "Have a great day! 😊\n"
        "Don't forget to check out when you leave."
    ),
    'already_checked_in': (
        "⚠️ **Already Checked In**\n\n"
        "You already checked in today at {time}.\n\n"
        "Use /checkout when you're ready to leave."
    ),

    # Check-out
    'checkout_prompt': (
        "🚪 **Check-Out Process**\n\n"
        "Please share your location to check out.\n\n"
        "⚠️ You must be within {radius}m of school.\n\n"
        "Tap the button below to share your location."
    ),
    'checkout_success': (
        "🚪 **Check-Out Successful!**\n\n"
        "🕐 Check-out: {checkout_time}\n"
        "🕐 Check-in: {checkin_time}\n"
        "⏱ Total hours: {hours}h\n"
        "📍 Distance: {distance}m from school\n\n"
        "Great work today! 👏"
    ),
    'not_checked_in': (
        "⚠️ **Not Checked In**\n\n"
        "You haven't checked in yet today.\n\n"
        "Use /checkin first to mark your arrival."
    ),
    'already_checked_out': (
        "⚠️ **Already Checked Out**\n\n"
        "You have already completed your attendance for today.\n\n"
        "See you tomorrow! 👋"
    ),

    # Status
    'status_not_checked_in': (
        "📅 **Today's Status**\n\n"
        "❌ Not checked in yet\n\n"
        "Use /checkin to mark your attendance"
    ),
    'status_checked_in': (
        "📅 **Today's Status**\n\n"
        "✅ Checked in: {checkin_time}\n"
        "⏳ Still checked in\n"
        "📍 Don't forget to check out!"
    ),
    'status_complete': (
        "📅 **Today's Status**\n\n"
        "✅ Checked in: {checkin_time}\n"
        "🚪 Checked out: {checkout_time}\n"
        "⏱ Total hours: {hours}h\n"
        "📍 Status: Complete ✅"
    ),

    # History
    'history_empty': (
        "📊 **Attendance History**\n\n"
        "No attendance records found.\n"
        "Use /checkin to start tracking your attendance."
    ),
    'history_header': "📊 **Attendance History** (Last 7 days)\n\n",

    # Language
    'language_select': (
        "🌍 **Select Your Language**\n\n"
        "Choose your preferred language:"
    ),
    'language_changed': "✅ Language changed to English",

    # Errors
    'error_distance': (
        "❌ **Too Far From School**\n\n"
        "📍 Your distance: {distance}m\n"
        "📏 Required: Within {radius}m\n"
        "🚶 You need to be {diff}m closer\n\n"
        "Please move closer to the school and try again."
    ),
    'error_weekend': (
        "📅 **Weekend Mode**\n\n"
        "⚠️ Attendance system is only active on weekdays (Monday-Friday).\n\n"
        "Enjoy your weekend! 🎉"
    ),
    'error_not_registered': (
        "⚠️ **Not Registered**\n\n"
        "Please use /start to register first."
    ),
    'error_admin_only': (
        "⛔️ **Access Denied**\n\n"
        "This command is only available to administrators.\n"
        "Contact your school admin for access."
    ),
    'error_general': (
        "⚠️ An error occurred while processing your request.\n"
        "Please try again later or contact an administrator."
    ),
    'error_invalid_location': "❌ Invalid location coordinates. Please try again.",
    'error_location_validation': "❌ Error validating location. Please try again.",
    'error_checkin_failed': "❌ Error recording check-in. Please try again or contact admin.",
    'error_checkout_failed': "❌ Error recording check-out. Please try again or contact admin.",

    # Buttons
    'btn_share_location': "📍 Share My Location",
    'btn_cancel': "❌ Cancel",
    'btn_english': "🇬🇧 English",
    'btn_russian': "🇷🇺 Русский",
    'btn_uzbek': "🇺🇿 O'zbek",

    # Misc
    'operation_cancelled': "❌ Operation cancelled.",
    'yes': "Yes ✅",
    'no': "No",
    'na': "N/A",
}
