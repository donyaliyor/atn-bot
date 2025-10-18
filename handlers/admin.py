"""
Admin panel handlers for attendance management.
Provides reports, CSV export, and user management.
"""
import logging
import csv
import io
from datetime import datetime, date, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import Config
from database.models import Attendance, Teacher, AdminLog
from locales import get_message
from utils.decorators import admin_only

logger = logging.getLogger(__name__)


@admin_only
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show admin panel with inline buttons for various actions.
    """
    user = update.effective_user
    lang = Teacher.get_language(user.id)

    keyboard = [
        [
            InlineKeyboardButton("📊 Today's Report", callback_data="admin_today"),
            InlineKeyboardButton("📅 Weekly Report", callback_data="admin_week")
        ],
        [
            InlineKeyboardButton("📥 Export CSV (Today)", callback_data="admin_csv_today"),
            InlineKeyboardButton("📥 Export CSV (Week)", callback_data="admin_csv_week")
        ],
        [
            InlineKeyboardButton("👥 User List", callback_data="admin_users"),
            InlineKeyboardButton("📈 Statistics", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton("🔍 Search User", callback_data="admin_search")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    message = get_message(lang, 'admin_panel_welcome')

    await update.message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

    # Log admin action
    AdminLog.log_action(user.id, "accessed_admin_panel")


async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle admin panel button callbacks"""
    query = update.callback_query
    user = query.from_user
    lang = Teacher.get_language(user.id)

    # Verify admin status
    if not Config.is_admin(user.id):
        await query.answer(get_message(lang, 'error_admin_only'), show_alert=True)
        return

    await query.answer()

    action = query.data.replace('admin_', '')

    if action == 'today':
        await send_today_report(query, lang)
    elif action == 'week':
        await send_week_report(query, lang)
    elif action == 'csv_today':
        await send_csv_export(query, lang, 'today')
    elif action == 'csv_week':
        await send_csv_export(query, lang, 'week')
    elif action == 'users':
        await send_user_list(query, lang)
    elif action == 'stats':
        await send_statistics(query, lang)
    elif action == 'search':
        await query.edit_message_text(
            get_message(lang, 'admin_search_prompt'),
            parse_mode='Markdown'
        )
        context.user_data['awaiting_admin_search'] = True


async def send_today_report(query, lang: str) -> None:
    """Send today's attendance report"""
    today = date.today()
    records = Attendance.get_daily_report(today)

    if not records:
        message = get_message(lang, 'admin_no_data_today')
        await query.edit_message_text(message, parse_mode='Markdown')
        return

    # Build report
    message = get_message(lang, 'admin_report_today', date=today.strftime('%Y-%m-%d'))
    message += "\n\n"

    checked_in = 0
    checked_out = 0

    for record in records:
        name = f"{record['first_name']} {record['last_name'] or ''}".strip()
        check_in_time = datetime.fromisoformat(record['check_in_time']).strftime('%H:%M')

        if record['check_out_time']:
            check_out_time = datetime.fromisoformat(record['check_out_time']).strftime('%H:%M')
            hours = record['total_hours']
            message += f"✅ {name}\n   ⏰ {check_in_time} → {check_out_time} ({hours:.1f}h)\n\n"
            checked_out += 1
        else:
            message += f"🔵 {name}\n   ⏰ {check_in_time} → ⏳ Still working\n\n"
            checked_in += 1

    message += f"\n📊 **Summary:**\n"
    message += f"Total: {len(records)} teachers\n"
    message += f"Checked in: {checked_in + checked_out}\n"
    message += f"Still working: {checked_in}\n"
    message += f"Completed: {checked_out}"

    await query.edit_message_text(message, parse_mode='Markdown')

    # Log action
    AdminLog.log_action(query.from_user.id, "viewed_today_report")


async def send_week_report(query, lang: str) -> None:
    """Send weekly attendance report"""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    message = get_message(
        lang,
        'admin_report_week',
        start_date=week_start.strftime('%Y-%m-%d'),
        end_date=today.strftime('%Y-%m-%d')
    )
    message += "\n\n"

    # Get all teachers
    teachers = Teacher.get_all_active()

    for teacher in teachers:
        name = f"{teacher['first_name']} {teacher['last_name'] or ''}".strip()
        user_id = teacher['user_id']

        # Get week history
        history = Attendance.get_user_history(user_id, limit=7)
        week_records = [r for r in history if datetime.fromisoformat(r['date']).date() >= week_start]

        if week_records:
            total_hours = sum(r['total_hours'] or 0 for r in week_records)
            days_worked = len(week_records)
            message += f"👤 {name}: {days_worked} days, {total_hours:.1f}h total\n"

    await query.edit_message_text(message, parse_mode='Markdown')

    # Log action
    AdminLog.log_action(query.from_user.id, "viewed_week_report")


async def send_csv_export(query, lang: str, period: str) -> None:
    """Export attendance data to CSV"""
    # Get data based on period
    if period == 'today':
        records = Attendance.get_daily_report(date.today())
        filename = f"attendance_{date.today().strftime('%Y-%m-%d')}.csv"
    else:  # week
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

        # Get all records for the week
        records = []
        for i in range(7):
            day = week_start + timedelta(days=i)
            records.extend(Attendance.get_daily_report(day))

        filename = f"attendance_week_{week_start.strftime('%Y-%m-%d')}.csv"

    if not records:
        await query.answer(get_message(lang, 'admin_no_data_export'), show_alert=True)
        return

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        'Date', 'User ID', 'Username', 'First Name', 'Last Name',
        'Check-in Time', 'Check-out Time', 'Total Hours', 'Status'
    ])

    # Write data
    for record in records:
        check_in = datetime.fromisoformat(record['check_in_time']).strftime('%Y-%m-%d %H:%M:%S')
        check_out = ''
        if record['check_out_time']:
            check_out = datetime.fromisoformat(record['check_out_time']).strftime('%Y-%m-%d %H:%M:%S')

        writer.writerow([
            record['date'],
            record['user_id'],
            record['username'] or '',
            record['first_name'],
            record['last_name'] or '',
            check_in,
            check_out,
            f"{record['total_hours']:.2f}" if record['total_hours'] else '',
            record['status']
        ])

    # Send CSV file
    output.seek(0)
    csv_bytes = io.BytesIO(output.getvalue().encode('utf-8'))
    csv_bytes.name = filename

    await query.message.reply_document(
        document=csv_bytes,
        filename=filename,
        caption=get_message(lang, 'admin_csv_export_success', filename=filename)
    )

    await query.answer(get_message(lang, 'admin_csv_sent'), show_alert=False)

    # Log action
    AdminLog.log_action(query.from_user.id, f"exported_csv_{period}", details=filename)


async def send_user_list(query, lang: str) -> None:
    """Send list of all users"""
    teachers = Teacher.get_all_active()

    message = get_message(lang, 'admin_user_list_header', count=len(teachers))
    message += "\n\n"

    for teacher in teachers:
        name = f"{teacher['first_name']} {teacher['last_name'] or ''}".strip()
        username = f"@{teacher['username']}" if teacher['username'] else "No username"
        admin_badge = " 🔑" if teacher['is_admin'] else ""
        lang_badge = f" [{teacher['language'].upper()}]"

        message += f"👤 {name} {admin_badge}{lang_badge}\n"
        message += f"   ID: `{teacher['user_id']}` | {username}\n\n"

    await query.edit_message_text(message, parse_mode='Markdown')

    # Log action
    AdminLog.log_action(query.from_user.id, "viewed_user_list")


async def send_statistics(query, lang: str) -> None:
    """Send database statistics"""
    from database.db import get_db_stats

    stats = get_db_stats()
    teachers = Teacher.get_all_active()

    # Get today's stats
    today_records = Attendance.get_daily_report(date.today())
    checked_in_today = len([r for r in today_records if not r['check_out_time']])
    completed_today = len([r for r in today_records if r['check_out_time']])

    message = get_message(lang, 'admin_stats_header')
    message += f"\n\n**Database:**\n"
    message += f"👥 Total Teachers: {stats['teachers']}\n"
    message += f"✅ Active Teachers: {len(teachers)}\n"
    message += f"📝 Total Records: {stats['attendance_records']}\n"
    message += f"📋 Admin Logs: {stats['admin_logs']}\n\n"

    message += f"**Today ({date.today().strftime('%Y-%m-%d')}):**\n"
    message += f"🔵 Currently Working: {checked_in_today}\n"
    message += f"✅ Completed: {completed_today}\n"
    message += f"📊 Total Check-ins: {len(today_records)}\n\n"

    message += f"**Configuration:**\n"
    message += f"📍 Location: ({Config.SCHOOL_LATITUDE:.4f}, {Config.SCHOOL_LONGITUDE:.4f})\n"
    message += f"📏 Radius: {Config.RADIUS_METERS}m\n"
    message += f"🌍 Languages: {', '.join(Config.SUPPORTED_LANGUAGES)}\n"
    message += f"🔧 DB: `{Config.DB_PATH}`"

    await query.edit_message_text(message, parse_mode='Markdown')

    # Log action
    AdminLog.log_action(query.from_user.id, "viewed_statistics")
