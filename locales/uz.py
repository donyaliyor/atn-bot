"""
Uzbek language translations.
"""

MESSAGES = {
    # Welcome & Start
    'welcome': (
        "👋 Xush kelibsiz, {first_name}!\n\n"
        "🏫 **Davomat Bot**\n\n"
        "Bu bot o'qituvchilarning davomatini manzil tekshiruvi bilan kuzatishga yordam beradi.\n\n"
        "📍 Belgilash uchun maktabdan {radius}m radius ichida bo'lishingiz kerak.\n"
        "📅 Faqat ish kunlarida ishlaydi.\n\n"
        "🆔 Sizning ID: `{user_id}`\n"
        "👤 Ro'yxatdan o'tgan: {full_name}\n\n"
        "Buyruqlarni ko'rish uchun /help dan foydalaning yoki quyidagi menyu tugmalarini bosing."
    ),

    # Help
    'help_user': (
        "📚 **Mavjud buyruqlar:**\n\n"
        "**Barcha foydalanuvchilar uchun:**\n"
        "/start - Botni ishga tushirish va ro'yxatdan o'tish\n"
        "/help - Yordam ko'rsatish\n"
        "/myid - ID ni ko'rsatish\n"
        "/checkin - Kelish vaqtini belgilash ✅\n"
        "/checkout - Ketish vaqtini belgilash 🚪\n"
        "/status - Bugungi holatni ko'rish\n"
        "/history - Davomat tarixi\n"
        "/language - Tilni o'zgartirish 🌍\n"
        "/cancel - Operatsiyani bekor qilish\n"
    ),
    'help_admin': (
        "\n**Administrator buyruqlari:**\n"
        "/admin - Administrator paneli 🔐\n"
        "/stats - Ma'lumotlar bazasi statistikasi 📈\n"
    ),

    # User Info
    'myid': (
        "👤 **Sizning ma'lumotlaringiz:**\n\n"
        "🆔 Foydalanuvchi ID: `{user_id}`\n"
        "📝 Username: @{username}\n"
        "👔 Ism: {full_name}\n"
        "🌍 Til: {language}\n"
        "🔑 Administrator: {admin_status}\n\n"
        "💡 Administrator ro'yxatiga qo'shish uchun ID ni saqlang"
    ),

    # Check-in
    'checkin_prompt': (
        "📍 **Kelish vaqtini belgilash**\n\n"
        "Iltimos, manzilingizni yuboring.\n\n"
        "⚠️ Maktabdan {radius}m radius ichida bo'lishingiz kerak:\n"
        "📍 {school_location}\n\n"
        "Manzilni yuborish uchun quyidagi tugmani bosing."
    ),
    'checkin_success': (
        "✅ **Kelish vaqti belgilandi!**\n\n"
        "🕐 Vaqt: {time}\n"
        "📍 Masofa: maktabdan {distance}m\n"
        "📅 Sana: {date}\n\n"
        "Yaxshi kun! 😊\n"
        "Ketishda belgilashni unutmang."
    ),
    'already_checked_in': (
        "⚠️ **Kelish vaqti allaqachon belgilangan**\n\n"
        "Siz bugun {time} da kelishingizni belgilagansiz.\n\n"
        "Ketish uchun /checkout dan foydalaning."
    ),

    # Check-out
    'checkout_prompt': (
        "🚪 **Ketish vaqtini belgilash**\n\n"
        "Iltimos, manzilingizni yuboring.\n\n"
        "⚠️ Maktabdan {radius}m radius ichida bo'lishingiz kerak.\n\n"
        "Quyidagi tugmani bosing."
    ),
    'checkout_success': (
        "🚪 **Ketish vaqti belgilandi!**\n\n"
        "🕐 Ketish: {checkout_time}\n"
        "🕐 Kelish: {checkin_time}\n"
        "⏱ Jami soatlar: {hours}s\n"
        "📍 Masofa: maktabdan {distance}m\n\n"
        "Ajoyib ish! 👏"
    ),
    'not_checked_in': (
        "⚠️ **Kelish vaqti belgilanmagan**\n\n"
        "Siz hali bugun kelishingizni belgilamadingiz.\n\n"
        "Avval /checkin dan foydalaning."
    ),
    'already_checked_out': (
        "⚠️ **Ketish vaqti allaqachon belgilangan**\n\n"
        "Siz bugungi ishingizni yakunladingiz.\n\n"
        "Ertaga ko'rishguncha! 👋"
    ),

    # Status
    'status_not_checked_in': (
        "📅 **Bugungi holat**\n\n"
        "❌ Hali kelish vaqti belgilanmagan\n\n"
        "/checkin dan foydalaning"
    ),
    'status_checked_in': (
        "📅 **Bugungi holat**\n\n"
        "✅ Kelish: {checkin_time}\n"
        "⏳ Hali ishdasiz\n"
        "📍 Ketishni belgilashni unutmang!"
    ),
    'status_complete': (
        "📅 **Bugungi holat**\n\n"
        "✅ Kelish: {checkin_time}\n"
        "🚪 Ketish: {checkout_time}\n"
        "⏱ Jami soatlar: {hours}s\n"
        "📍 Holat: Yakunlandi ✅"
    ),

    # History
    'history_empty': (
        "📊 **Davomat tarixi**\n\n"
        "Yozuvlar topilmadi.\n"
        "Kuzatishni boshlash uchun /checkin dan foydalaning."
    ),
    'history_header': "📊 **Davomat tarixi** (Oxirgi 7 kun)\n\n",

    # Language
    'language_select': (
        "🌍 **Tilni tanlang**\n\n"
        "Tilni tanlang:"
    ),
    'language_changed': "✅ Til o'zbekchaga o'zgartirildi",
    'language_changing': "⏳ Til o'zgartirilmoqda...",
    'menu_updated': "✅ Menyu yangilandi! Tez kirish uchun quyidagi tugmalardan foydalaning.",

    # Admin Panel
    'admin_panel_welcome': "🔐 **Administrator paneli**\n\nHarakatni tanlang:",
    'admin_no_data_today': "📭 Bugun uchun davomat yozuvlari yo'q.",
    'admin_no_data_export': "📭 Bu davr uchun eksport qilish uchun ma'lumotlar yo'q.",
    'admin_report_today': "📊 **Davomat hisoboti**\n📅 Sana: {date}",
    'admin_report_week': "📊 **Haftalik hisobot**\n📅 {start_date} - {end_date}",
    'admin_csv_export_success': "✅ Davomat ma'lumotlari eksport qilindi\n📄 {filename}",
    'admin_csv_sent': "📧 CSV fayl muvaffaqiyatli yuborildi",
    'admin_user_list_header': "👥 **Foydalanuvchilar ro'yxati** (jami {count})",
    'admin_stats_header': "📊 **Tizim statistikasi**",
    'admin_search_prompt': "🔍 Qidirish uchun foydalanuvchi ID yoki username yuboring...",

    # Errors
    'error_distance': (
        "❌ **Maktabdan juda uzoqsiz**\n\n"
        "📍 Sizning masofangiz: {distance}m\n"
        "📏 Kerak: {radius}m ichida\n"
        "🚶 {diff}m yaqinlashishingiz kerak\n\n"
        "Maktabga yaqinlashib, qayta urinib ko'ring."
    ),
    'error_weekend': (
        "📅 **Dam olish kuni**\n\n"
        "⚠️ Davomat tizimi faqat ish kunlarida ishlaydi (Dushanba-Juma).\n\n"
        "Yaxshi dam oling! 🎉"
    ),
    'error_not_registered': (
        "⚠️ **Ro'yxatdan o'tmagan**\n\n"
        "Iltimos, avval /start dan foydalaning."
    ),
    'error_admin_only': (
        "⛔️ **Ruxsat berilmagan**\n\n"
        "Bu buyruq faqat administratorlar uchun.\n"
        "Maktab administratoriga murojaat qiling."
    ),
    'error_general': (
        "⚠️ So'rovni qayta ishlashda xatolik yuz berdi.\n"
        "Keyinroq urinib ko'ring yoki administratorga murojaat qiling."
    ),
    'error_invalid_location': "❌ Noto'g'ri koordinatalar. Qayta urinib ko'ring.",
    'error_location_validation': "❌ Manzilni tekshirishda xatolik yuz berdi. Qayta urinib ko'ring.",
    'error_checkin_failed': "❌ Kelishni saqlashda xatolik yuz berdi. Administratorga murojaat qiling.",
    'error_checkout_failed': "❌ Ketishni saqlashda xatolik yuz berdi. Administratorga murojaat qiling.",

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
    'btn_share_location': "📍 Manzilni yuborish",
    'btn_cancel': "❌ Bekor qilish",
    'btn_english': "🇬🇧 English",
    'btn_russian': "🇷🇺 Русский",
    'btn_uzbek': "🇺🇿 O'zbek",

    # Misc
    'operation_cancelled': "❌ Operatsiya bekor qilindi.",
    'yes': "Ha ✅",
    'no': "Yo'q",
    'na': "M/Y",
}
