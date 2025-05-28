import requests
import telebot

# توكن البوت
TOKEN = '7458138039:AAFSX74H91fXoRgwfqzOzp_qu9QO6vVXFmU'
bot = telebot.TeleBot(TOKEN)

# مفتاح API الخاص بـ LeakCheck
API_KEY = '858c246c89cc9914baa97d3dc2c21a6cd03e6222'

# قائمة المستخدمين المصرح لهم
authorized_users = set()

# معرفات المالكين
OWNERS = {6358035274, 7672037992}

# أمر لإضافة مستخدم
@bot.message_handler(commands=['add_user'])
def add_user(message):
    if message.from_user.id in OWNERS:
        try:
            parts = message.text.split()
            user_id = int(parts[1])
            authorized_users.add(user_id)
            bot.reply_to(message, f"✅ تم إضافة المستخدم {user_id} بنجاح.")
        except (IndexError, ValueError):
            bot.reply_to(message, "❌ الرجاء إدخال معرف مستخدم صحيح بعد الأمر.")
    else:
        bot.reply_to(message, "🚫 ليس لديك صلاحية لإضافة مستخدمين.")

# أمر لإزالة مستخدم
@bot.message_handler(commands=['remove_user'])
def remove_user(message):
    if message.from_user.id in OWNERS:
        try:
            parts = message.text.split()
            user_id = int(parts[1])
            authorized_users.discard(user_id)
            bot.reply_to(message, f"✅ تم إزالة المستخدم {user_id} بنجاح.")
        except (IndexError, ValueError):
            bot.reply_to(message, "❌ الرجاء إدخال معرف مستخدم صحيح بعد الأمر.")
    else:
        bot.reply_to(message, "🚫 ليس لديك صلاحية لإزالة مستخدمين.")

# أمر للتحقق من البيانات المسربة
@bot.message_handler(commands=['Jid'])
def handle_leakcheck_query(message):
    if message.from_user.id in authorized_users or message.from_user.id in OWNERS:
        try:
            parts = message.text.split()
            query = parts[1]
        except IndexError:
            bot.reply_to(message, "❗ الرجاء إدخال البريد الإلكتروني أو اسم المستخدم بعد الأمر.")
            return

        headers = {
            'Accept': 'application/json',
            'X-API-Key': API_KEY
        }

        response = requests.get(f'https://leakcheck.io/api/v2/query/{query}', headers=headers)

        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success') and data['found'] > 0:
                    reply_message = f"🔍 نتائج البحث عن: {query}\n\n"
                    for result in data['result']:
                        source = result.get('source', {})
                        source_name = source.get('name', 'غير معروف')
                        breach_date = source.get('breach_date', 'غير محدد')
                        ip_address = result.get('ip', 'غير متوفر')
                        origin = result.get('origin', 'غير معروف')

                        result_message = (
                            f"📛 المصدر: {source_name}\n"
                            f"📅 تاريخ التسريب: {breach_date}\n"
                            f"🌐 عنوان IP: {ip_address}\n"
                            f"🌐 موقع التسريب: {origin}\n"
                            f"📧 بريد إلكتروني: {result.get('email', 'غير متوفر')}\n"
                            f"👤 اسم المستخدم: {result.get('username', 'غير متوفر')}\n"
                            f"🔑 كلمة المرور: {result.get('password', 'غير متوفر')}\n"
                            f"👥 الاسم الأول: {result.get('first_name', 'غير متوفر')}\n"
                            f"👥 الاسم الأخير: {result.get('last_name', 'غير متوفر')}\n"
                            f"🎂 تاريخ الميلاد: {result.get('dob', 'غير متوفر')}\n"
                            f"🏠 العنوان: {result.get('address', 'غير متوفر')}\n"
                            f"📦 الرمز البريدي: {result.get('zip', 'غير متوفر')}\n"
                            f"📞 الهاتف: {result.get('phone', 'غير متوفر')}\n"
                            f"📝 الاسم الكامل: {result.get('name', 'غير متوفر')}\n"
                            "-----------------------------------\n\n"
                        )
                        reply_message += result_message

                    bot.reply_to(message, reply_message)
                else:
                    bot.reply_to(message, "❌ لا توجد نتائج لهذا البحث.")
            except ValueError:
                bot.reply_to(message, "⚠️ لم يتم استلام رد بصيغة JSON.")
        else:
            if response.status_code == 401:
                bot.reply_to(message, "❌ مفتاح API مفقود أو غير صالح.")
            elif response.status_code == 400:
                bot.reply_to(message, "❌ طلب غير صالح. تحقق من صيغة الاستعلام.")
            elif response.status_code == 403:
                bot.reply_to(message, "🚫 تم رفض الوصول. ربما تحتاج إلى خطة مفعّلة.")
            elif response.status_code == 429:
                bot.reply_to(message, "⚠️ تم إرسال الكثير من الطلبات. حاول لاحقاً.")
            elif response.status_code == 422:
                bot.reply_to(message, "❗ لم يتم تحديد نوع البحث تلقائياً. الرجاء تحديده.")
            else:
                bot.reply_to(message, f"❌ فشل الاتصال بـ LeakCheck. رمز الحالة: {response.status_code}")
    else:
        bot.reply_to(message, "🚫 ليس لديك صلاحية لاستخدام هذا الأمر.")

# تشغيل البوت
bot.polling()
