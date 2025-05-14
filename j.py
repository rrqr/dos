import os
import requests
import telebot

# Bot access token
TOKEN = '7333263562:AAE7SGKtGMwlbkxNroPyh3MBvY8EUc2PCmU'
bot = telebot.TeleBot(TOKEN)

# LeakCheck API key
API_KEY = '370349b14a81c9a1fbf97ec4d41e1dc5a5ea8d58'

# List of authorized user IDs
authorized_users = set()

# Owner ID
OWNER_ID = 6358035274

@bot.message_handler(commands=['add_user'])
def add_user(message):
    if message.from_user.id == OWNER_ID:
        try:
            parts = message.text.split()
            user_id = int(parts[1])
            authorized_users.add(user_id)
            bot.reply_to(message, f"User {user_id} added successfully.")
        except (IndexError, ValueError):
            bot.reply_to(message, "Please provide a valid user ID to add.")
    else:
        bot.reply_to(message, "You are not authorized to add users.")

@bot.message_handler(commands=['remove_user'])
def remove_user(message):
    if message.from_user.id == OWNER_ID:
        try:
            parts = message.text.split()
            user_id = int(parts[1])
            authorized_users.discard(user_id)
            bot.reply_to(message, f"User {user_id} removed successfully.")
        except (IndexError, ValueError):
            bot.reply_to(message, "Please provide a valid user ID to remove.")
    else:
        bot.reply_to(message, "You are not authorized to remove users.")

@bot.message_handler(commands=['Jid'])
def handle_allD_command(message):
    if message.from_user.id in authorized_users or message.from_user.id == OWNER_ID:
        try:
            parts = message.text.split()
            query = parts[1]
        except IndexError:
            bot.reply_to(message, "Please enter the email or username after the command.")
            return

        headers = {
            'Accept': 'application/json',
            'X-API-Key': API_KEY
        }

        try:
            response = requests.get(f'https://leakcheck.io/api/v2/query/{query}', headers=headers)
        except Exception as e:
            bot.reply_to(message, f"Connection error: {e}")
            return

        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success') and data.get('found', 0) > 0:
                    reply_message = f"🔍 Search results for: {query}\nTotal found: {data['found']}\n\n"

                    for result in data['result']:
                        source = result.get('source', {})
                        source_name = source.get('name', 'Unknown')
                        breach_date = source.get('breach_date', 'None')
                        ip_address = result.get('ip', 'N/A')
                        origin = result.get('origin', 'N/A')

                        result_message = (
                            f"📛 Source: {source_name}\n"
                            f"📅 Breach Date: {breach_date}\n"
                            f"🌐 IP Address: {ip_address}\n"
                            f"🌐 Leak Location: {origin}\n"
                            f"📧 Email: {result.get('email', 'N/A')}\n"
                            f"👤 Username: {result.get('username', 'N/A')}\n"
                            f"🔑 Password: {result.get('password', 'N/A')}\n"
                            f"👥 First Name: {result.get('first_name', 'N/A')}\n"
                            f"👥 Last Name: {result.get('last_name', 'N/A')}\n"
                            f"🎂 Date of Birth: {result.get('dob', 'N/A')}\n"
                            f"🏠 Address: {result.get('address', 'N/A')}\n"
                            f"📦 Zip Code: {result.get('zip', 'N/A')}\n"
                            f"📞 Phone: {result.get('phone', 'N/A')}\n"
                            f"📝 Name: {result.get('name', 'N/A')}\n"
                            "-----------------------------------\n\n"
                        )

                        reply_message += result_message

                    # كتابة النتائج إلى ملف
                    filename = f"{query}_results.txt"
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(reply_message)

                    # إرسال الملف للمستخدم
                    with open(filename, "rb") as f:
                        bot.send_document(message.chat.id, f)

                    # حذف الملف بعد الإرسال
                    os.remove(filename)

                else:
                    bot.reply_to(message, "No results found for this search.")
            except Exception as e:
                bot.reply_to(message, f"Error processing data: {str(e)}")
        else:
            status_messages = {
                401: "Missing or invalid API key.",
                400: "Invalid request format.",
                403: "Access denied – check your subscription.",
                429: "Too many requests – slow down.",
                422: "Search type could not be determined.",
            }
            bot.reply_to(message, status_messages.get(response.status_code, f"Failed to connect. Status code: {response.status_code}"))
    else:
        bot.reply_to(message, "You are not authorized to perform this action.")

# Start the bot
bot.polling()
