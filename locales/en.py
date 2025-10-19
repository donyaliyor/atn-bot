"""
English language translations - Clean UI version with minimal emojis.
PHASE 2: Added notification and schedule messages.
"""

MESSAGES = {
    # Welcome & Start
    'welcome': (
        "Welcome, {first_name}!\n\n"
        "**Attendance Bot**\n\n"
        "Track your attendance with location verification.\n\n"
        "**Requirements:**\n"
        "• Location: Within {radius}m of school\n"
        "• Schedule: Weekdays only\n\n"
        "**Your Profile:**\n"
        "User ID: `{user_id}`\n"
        "Name: {full_name}\n\n"
        "Use /help to see available commands or the menu buttons below."
    ),

    # Help
    'help_user': (
        "**Available Commands**\n\n"
        "**Attendance:**\n"
        "/checkin - Mark arrival with location\n"
        "/checkout - Mark departure with location\n"
        "/status - View today's status\n"
        "/history - View last 7 days\n\n"
        "**Settings:**\n"
        "/language - Change language\n"
        "/notifications - Toggle reminders\n"
        "/myid - Show your user ID\n"
        "/help - Show this help\n"
        "/cancel - Cancel operation\n"
    ),
    'help_admin': (
        "\n**Admin Commands:**\n"
        "/admin - Access admin panel\n"
        "/schedule - View work schedule\n"
        "/stats - View statistics\n"
    ),

    # User Info
    'myid': (
        "**Your Information**\n\n"
        "User ID: `{user_id}`\n"
        "Username: @{username}\n"
        "Name: {full_name}\n"
        "Language: {language}\n"
        "Admin: {admin_status}\n\n"
        "Save your User ID to request admin access."
    ),

    # Check-in
    'checkin_prompt': (
        "**Check-In Process**\n\n"
        "Share your location to check in.\n\n"
        "**Requirements:**\n"
        "• Distance: Within {radius}m of school\n"
        "• Location: {school_location}\n\n"
        "Tap the button below to share your location."
    ),
    'checkin_success': (
        "✅ **Check-In Successful**\n\n"
        "Time: {time}\n"
        "Date: {date}\n"
        "Distance: {distance}m from school\n\n"
        "Have a great day! Remember to check out when you leave."
    ),
    'already_checked_in': (
        "**Already Checked In**\n\n"
        "You checked in today at {time}.\n\n"
        "Use /checkout when you're ready to leave."
    ),

    # Check-out
    'checkout_prompt': (
        "**Check-Out Process**\n\n"
        "Share your location to check out.\n\n"
        "Required: Within {radius}m of school\n\n"
        "Tap the button below."
    ),
    'checkout_success': (
        "✅ **Check-Out Successful**\n\n"
        "Check-in: {checkin_time}\n"
        "Check-out: {checkout_time}\n"
        "Total hours: {hours}h\n"
        "Distance: {distance}m\n\n"
        "Great work today!"
    ),
    'not_checked_in': (
        "**Not Checked In**\n\n"
        "You haven't checked in yet today.\n\n"
        "Use /checkin to mark your arrival."
    ),
    'already_checked_out': (
        "**Already Checked Out**\n\n"
        "You've completed your attendance for today.\n\n"
        "See you tomorrow!"
    ),

    # Status
    'status_not_checked_in': (
        "**Today's Status**\n\n"
        "Status: Not checked in\n\n"
        "Use /checkin to mark your attendance."
    ),
    'status_checked_in': (
        "**Today's Status**\n\n"
        "Checked in: {checkin_time}\n"
        "Status: Still checked in\n\n"
        "Don't forget to check out!"
    ),
    'status_complete': (
        "**Today's Status**\n\n"
        "Checked in: {checkin_time}\n"
        "Checked out: {checkout_time}\n"
        "Total hours: {hours}h\n"
        "Status: Complete"
    ),

    # History
    'history_empty': (
        "**Attendance History**\n\n"
        "No attendance records found.\n\n"
        "Use /checkin to start tracking your attendance."
    ),
    'history_header': "**Attendance History**\nLast 7 days\n\n",

    # Language
    'language_select': (
        "**Select Your Language**\n\n"
        "Choose your preferred language:"
    ),
    'language_changed': "✅ Language changed to English",
    'language_changing': "Changing language...",
    'menu_updated': "✅ Menu updated! Use the buttons below for quick access.",

    # Admin Panel
    'admin_panel_welcome': "**Admin Panel**\n\nSelect an action:",
    'admin_no_data_today': "No attendance records for today.",
    'admin_no_data_export': "No data to export for this period.",
    'admin_report_today': "**Attendance Report**\nDate: {date}",
    'admin_report_week': "**Weekly Report**\n{start_date} to {end_date}",
    'admin_csv_export_success': "✅ Attendance data exported\n{filename}",
    'admin_csv_sent': "CSV file sent successfully",
    'admin_user_list_header': "**User List**\n{count} total",
    'admin_stats_header': "**System Statistics**",
    'admin_search_prompt': "Send user ID or username to search...",

    # Errors
    'error_distance': (
        "**Too Far From School**\n\n"
        "Your distance: {distance}m\n"
        "Required: Within {radius}m\n"
        "Difference: {diff}m too far\n\n"
        "Please move closer and try again."
    ),
    'error_weekend': (
        "**Weekend Mode**\n\n"
        "Attendance system is only active on weekdays (Monday-Friday).\n\n"
        "Enjoy your weekend!"
    ),
    'error_not_registered': (
        "**Not Registered**\n\n"
        "Please use /start to register first."
    ),
    'error_admin_only': (
        "**Access Denied**\n\n"
        "This command is only available to administrators.\n\n"
        "Contact your admin for access."
    ),
    'error_general': (
        "An error occurred while processing your request.\n\n"
        "Please try again or contact an administrator."
    ),
    'error_rate_limit': (
    "⏱️ **Please wait {seconds} seconds**\n\n"
    "You're sending commands too quickly. Please try again in a moment."
    ),
    'error_invalid_location': "Invalid location coordinates. Please try again.",
    'error_location_validation': "Error validating location. Please try again.",
    'error_checkin_failed': "Error recording check-in. Please try again or contact admin.",
    'error_checkout_failed': "Error recording check-out. Please try again or contact admin.",

    # Menu Buttons
    'btn_checkin': "Check In",
    'btn_checkout': "Check Out",
    'btn_status': "My Status",
    'btn_history': "History",
    'btn_language': "Language",
    'btn_help': "Help",
    'btn_admin': "Admin Panel",
    'btn_stats': "Statistics",

    # Other Buttons
    'btn_share_location': "Share My Location",
    'btn_cancel': "Cancel",
    'btn_english': "English",
    'btn_russian': "Русский",
    'btn_uzbek': "O'zbek",

    # Misc
    'operation_cancelled': "Operation cancelled.",
    'yes': "Yes",
    'no': "No",
    'na': "N/A",

    # ========================================================================
    # PHASE 2: Notification System & Work Schedule
    # ========================================================================

    # Notification Preferences
    'notification_settings': (
        "**Notification Settings**\n\n"
        "Current status: {status}\n\n"
        "**Notification Schedule:**\n"
        "• Morning Reminder: {morning_time}\n"
        "• Late Warning: {late_time}\n"
        "• Checkout Reminder: {checkout_time}\n"
        "• Forgotten Checkout: {forgotten_time}\n\n"
        "You will receive automatic reminders to maintain perfect attendance!"
    ),
    'notification_toggled': "✅ Notifications {status}",
    'notification_enabled': (
        "You will receive timely reminders:\n"
        "• Morning check-in reminder\n"
        "• Late arrival warning\n"
        "• Checkout reminder\n"
        "• Forgotten checkout alert"
    ),
    'notification_disabled': "You will not receive any reminders.",

    # Late Check-in
    'checkin_success_late': (
        "⚠️ **Late Check-In**\n\n"
        "Time: {time}\n"
        "Date: {date}\n"
        "Late by: {minutes_late} minutes\n"
        "Distance: {distance}m\n\n"
        "Please try to arrive on time tomorrow."
    ),

    # Admin Schedule View
    'schedule_info': (
        "**Work Schedule Configuration**\n\n"
        "**Work Hours:**\n"
        "• Start: {start_time}\n"
        "• End: {end_time}\n"
        "• Grace Period: {grace_period} minutes\n"
        "• Work Days: {work_days}\n\n"
        "**Notification Times:**\n"
        "• Morning Reminder: {morning_reminder}\n"
        "• Late Warning: {late_warning}\n"
        "• Checkout Reminder: {checkout_reminder}\n"
        "• Forgotten Checkout: {forgotten_checkout}\n\n"
        "💡 To update schedule, contact admin"
    ),

    # Notification Messages (sent by notification handlers)
    'notif_morning_reminder': (
        "🌅 **Good Morning!**\n\n"
        "Don't forget to check in when you arrive at school.\n"
        "Work starts at {start_time}."
    ),
    'notif_late_warning': (
        "⏰ **Late Check-In Warning**\n\n"
        "You haven't checked in yet.\n"
        "Grace period ends at {deadline}.\n"
        "Please check in now!"
    ),
    'notif_checkout_reminder': (
        "🏁 **Time to Check Out**\n\n"
        "Work day is ending soon ({end_time}).\n"
        "Remember to check out before leaving!"
    ),
    'notif_forgotten_checkout': (
        "🚨 **Forgotten Check-Out Alert**\n\n"
        "You forgot to check out!\n"
        "Please check out now to record your work hours."
    ),
}
