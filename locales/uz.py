"""
Uzbek language translations - Clean UI version with minimal emojis.
PHASE 2: Added notification and schedule messages.
"""

MESSAGES = {
    # Welcome & Start
    'welcome': (
        "Xush kelibsiz, {first_name}!\n\n"
        "**Davomat Bot**\n\n"
        "Davomatni manzil tekshiruvi bilan kuzating.\n\n"
        "**Talablar:**\n"
        "• Manzil: Maktabdan {radius}m radius ichida\n"
        "• Jadval: Faqat ish kunlarida\n\n"
        "**Sizning profilingiz:**\n"
        "Foydalanuvchi ID: `{user_id}`\n"
        "Ism: {full_name}\n\n"
        "Buyruqlarni ko'rish uchun /help dan foydalaning yoki quyidagi menyu tugmalarini bosing."
    ),

    # Help
    'help_user': (
        "**Mavjud buyruqlar**\n\n"
        "**Davomat:**\n"
        "/checkin - Kelish vaqtini belgilash\n"
        "/checkout - Ketish vaqtini belgilash\n"
        "/status - Bugungi holatni ko'rish\n"
        "/history - Oxirgi 7 kun tarixi\n\n"
        "**Sozlamalar:**\n"
        "/language - Tilni o'zgartirish\n"
        "/notifications - Eslatmalarni boshqarish\n"
        "/myid - ID ni ko'rsatish\n"
        "/help - Yordamni ko'rsatish\n"
        "/cancel - Operatsiyani bekor qilish\n"
    ),
    'help_admin': (
        "\n**Administrator buyruqlari:**\n"
        "/admin - Administrator paneli\n"
        "/schedule - Ish jadvali\n"
        "/stats - Statistika\n"
    ),

    # User Info
    'myid': (
        "**Sizning ma'lumotlaringiz**\n\n"
        "Foydalanuvchi ID: `{user_id}`\n"
        "Username: @{username}\n"
        "Ism: {full_name}\n"
        "Til: {language}\n"
        "Administrator: {admin_status}\n\n"
        "Administrator huquqlarini so'rash uchun ID ni saqlang."
    ),

    # Check-in
    'checkin_prompt': (
        "**Kelish vaqtini belgilash**\n\n"
        "Manzilingizni yuboring.\n\n"
        "**Talablar:**\n"
        "• Masofa: Maktabdan {radius}m radius ichida\n"
        "• Manzil: {school_location}\n\n"
        "Quyidagi tugmani bosing."
    ),
    'checkin_success': (
        "✅ **Kelish vaqti belgilandi**\n\n"
        "Vaqt: {time}\n"
        "Sana: {date}\n"
        "Masofa: maktabdan {distance}m\n\n"
        "Yaxshi kun! Ketishda belgilashni unutmang."
    ),
    'already_checked_in': (
        "**Kelish vaqti allaqachon belgilangan**\n\n"
        "Siz bugun {time} da kelishingizni belgilagansiz.\n\n"
        "Ketish uchun /checkout dan foydalaning."
    ),

    # Check-out
    'checkout_prompt': (
        "**Ketish vaqtini belgilash**\n\n"
        "Manzilingizni yuboring.\n\n"
        "Talab: Maktabdan {radius}m radius ichida\n\n"
        "Quyidagi tugmani bosing."
    ),
    'checkout_success': (
        "✅ **Ketish vaqti belgilandi**\n\n"
        "Kelish: {checkin_time}\n"
        "Ketish: {checkout_time}\n"
        "Jami soatlar: {hours}s\n"
        "Masofa: {distance}m\n\n"
        "Ajoyib ish!"
    ),
    'not_checked_in': (
        "**Kelish vaqti belgilanmagan**\n\n"
        "Siz hali bugun kelishingizni belgilamadingiz.\n\n"
        "Kelishni belgilash uchun /checkin dan foydalaning."
    ),
    'already_checked_out': (
        "**Ketish vaqti allaqachon belgilangan**\n\n"
        "Siz bugungi ishingizni yakunladingiz.\n\n"
        "Ertaga ko'rishguncha!"
    ),

    # Status
    'status_not_checked_in': (
        "**Bugungi holat**\n\n"
        "Holat: Kelish vaqti belgilanmagan\n\n"
        "Belgilash uchun /checkin dan foydalaning."
    ),
    'status_checked_in': (
        "**Bugungi holat**\n\n"
        "Kelish: {checkin_time}\n"
        "Holat: Hali ishdasiz\n\n"
        "Ketishni belgilashni unutmang!"
    ),
    'status_complete': (
        "**Bugungi holat**\n\n"
        "Kelish: {checkin_time}\n"
        "Ketish: {checkout_time}\n"
        "Jami soatlar: {hours}s\n"
        "Holat: Yakunlandi"
    ),

    # History
    'history_empty': (
        "**Davomat tarixi**\n\n"
        "Yozuvlar topilmadi.\n\n"
        "Kuzatishni boshlash uchun /checkin dan foydalaning."
    ),
    'history_header': "**Davomat tarixi**\nOxirgi 7 kun\n\n",

    # Language
    'language_select': (
        "**Tilni tanlang**\n\n"
        "Tilni tanlang:"
    ),
    'language_changed': "✅ Til o'zbekchaga o'zgartirildi",
    'language_changing': "Til o'zgartirilmoqda...",
    'menu_updated': "✅ Menyu yangilandi! Quyidagi tugmalardan foydalaning.",

    # Admin Panel
    'admin_panel_welcome': "**Administrator paneli**\n\nHarakatni tanlang:",
    'admin_no_data_today': "Bugun uchun davomat yozuvlari yo'q.",
    'admin_no_data_export': "Bu davr uchun eksport qilish uchun ma'lumotlar yo'q.",
    'admin_report_today': "**Davomat hisoboti**\nSana: {date}",
    'admin_report_week': "**Haftalik hisobot**\n{start_date} - {end_date}",
    'admin_csv_export_success': "✅ Ma'lumotlar eksport qilindi\n{filename}",
    'admin_csv_sent': "CSV fayl muvaffaqiyatli yuborildi",
    'admin_user_list_header': "**Foydalanuvchilar ro'yxati**\n{count} jami",
    'admin_stats_header': "**Tizim statistikasi**",
    'admin_search_prompt': "Qidirish uchun ID yoki username yuboring...",

    # Errors
    'error_distance': (
        "**Maktabdan juda uzoqsiz**\n\n"
        "Sizning masofangiz: {distance}m\n"
        "Kerak: {radius}m ichida\n"
        "Farq: {diff}m juda uzoq\n\n"
        "Yaqinlashib, qayta urinib ko'ring."
    ),
    'error_weekend': (
        "**Dam olish kuni**\n\n"
        "Davomat tizimi faqat ish kunlarida ishlaydi (Dushanba-Juma).\n\n"
        "Yaxshi dam oling!"
    ),
    'error_not_registered': (
        "**Ro'yxatdan o'tmagan**\n\n"
        "Iltimos, avval /start dan foydalaning."
    ),
    'error_admin_only': (
        "**Ruxsat berilmagan**\n\n"
        "Bu buyruq faqat administratorlar uchun.\n\n"
        "Administratorga murojaat qiling."
    ),
    'error_general': (
        "So'rovni qayta ishlashda xatolik yuz berdi.\n\n"
        "Keyinroq urinib ko'ring yoki administratorga murojaat qiling."
    ),
    'error_invalid_location': "Noto'g'ri koordinatalar. Qayta urinib ko'ring.",
    'error_location_validation': "Manzilni tekshirishda xatolik. Qayta urinib ko'ring.",
    'error_checkin_failed': "Kelishni saqlashda xatolik. Administratorga murojaat qiling.",
    'error_checkout_failed': "Ketishni saqlashda xatolik. Administratorga murojaat qiling.",

    # Menu Buttons
    'btn_checkin': "Kelish belgilash",
    'btn_checkout': "Ketish belgilash",
    'btn_status': "Mening holatim",
    'btn_history': "Tarix",
    'btn_language': "Til",
    'btn_help': "Yordam",
    'btn_admin': "Admin paneli",
    'btn_stats': "Statistika",

    # Other Buttons
    'btn_share_location': "Manzilni yuborish",
    'btn_cancel': "Bekor qilish",
    'btn_english': "English",
    'btn_russian': "Русский",
    'btn_uzbek': "O'zbek",

    # Misc
    'operation_cancelled': "Operatsiya bekor qilindi.",
    'yes': "Ha",
    'no': "Yo'q",
    'na': "M/Y",

    # ========================================================================
    # PHASE 2: Notification System & Work Schedule
    # ========================================================================

    # Notification Preferences
    'notification_settings': (
        "**Bildirishnoma sozlamalari**\n\n"
        "Joriy holat: {status}\n\n"
        "**Bildirishnoma jadvali:**\n"
        "• Ertalabki eslatma: {morning_time}\n"
        "• Kech qolish ogohlantirish: {late_time}\n"
        "• Ketish eslatmasi: {checkout_time}\n"
        "• Unutilgan ketish: {forgotten_time}\n\n"
        "Quyidagi tugma bilan bildirishnomalarni yoqing/o'chiring."
    ),
    'notification_toggled': "✅ Bildirishnomalar {status}",
    'notification_enabled': (
        "Siz o'z vaqtida eslatmalar olasiz:\n"
        "• Ertalabki kelish eslatmasi\n"
        "• Kech qolish haqida ogohlantirish\n"
        "• Ketish eslatmasi\n"
        "• Unutilgan ketish ogohlantirish"
    ),
    'notification_disabled': "Siz eslatmalar olmaysiz.",

    # Late Check-in
    'checkin_success_late': (
        "⚠️ **Kech qoldingiz**\n\n"
        "Vaqt: {time}\n"
        "Sana: {date}\n"
        "Kechikish: {minutes_late} daqiqa\n"
        "Masofa: {distance}m\n\n"
        "Iltimos, ertaga o'z vaqtida keling."
    ),

    # Admin Schedule View
    'schedule_info': (
        "**Ish jadvali sozlamalari**\n\n"
        "**Ish vaqti:**\n"
        "• Boshlanish: {start_time}\n"
        "• Tugash: {end_time}\n"
        "• Imtiyoz vaqti: {grace_period} daqiqa\n"
        "• Ish kunlari: {work_days}\n\n"
        "**Bildirishnoma vaqtlari:**\n"
        "• Ertalabki eslatma: {morning_reminder}\n"
        "• Kech qolish ogohlantirish: {late_warning}\n"
        "• Ketish eslatmasi: {checkout_reminder}\n"
        "• Unutilgan ketish: {forgotten_checkout}\n\n"
        "💡 Jadvalni o'zgartirish uchun adminga murojaat qiling"
    ),

    # Notification Messages (sent by notification handlers)
    'notif_morning_reminder': (
        "🌅 **Xayrli tong!**\n\n"
        "Maktabga yetganingizda belgilashni unutmang.\n"
        "Ish {start_time} da boshlanadi."
    ),
    'notif_late_warning': (
        "⏰ **Kech qolish ogohlantirish**\n\n"
        "Siz hali belgilanmadingiz.\n"
        "Imtiyoz vaqti {deadline} da tugaydi.\n"
        "Iltimos, hozir belgilang!"
    ),
    'notif_checkout_reminder': (
        "🏁 **Ketishni belgilash vaqti**\n\n"
        "Ish kuni tez orada tugaydi ({end_time}).\n"
        "Ketishdan oldin belgilashni unutmang!"
    ),
    'notif_forgotten_checkout': (
        "🚨 **Ketishni belgilashni unutdingiz!**\n\n"
        "Siz ketishni belgilashni unutdingiz!\n"
        "Iltimos, ish soatlarini qayd qilish uchun hozir belgilang."
    ),
}
