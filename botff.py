import requests
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Bot Token
TOKEN = os.getenv("TOKEN")

# ID الخاص بالمدير الذي يستطيع التواصل مع البوت في الخاص
ADMIN_ID = int(os.getenv("ADMIN_ID"))  # تأكد من تحويل القيمة إلى رقم

# Group ID where the bot will work
GROUP_ID = int(os.getenv("GROUP_ID"))  # تأكد من تحويل القيمة إلى رقم

# Function to format timestamps into a readable format
def format_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %I:%M %p") if timestamp else "Not Available"

# Function to fetch player data from the API
def get_player_data(uid):
    url = f"https://fox-api-lyart.vercel.app/info?id={uid}"
    r = requests.get(url)
    return r.json()

# Function to create a beautifully formatted message with player data
def create_formatted_text(data):
    formatted_text = f"""
┐──────معلومات لاعب──────┌
    
    🎮 Player Activity:
    ├─ Last Login: {format_time(data['basicInfo'].get('lastLoginAt'))}
    └─ Account Created: {format_time(data['basicInfo'].get('createAt'))}

    👤 Basic Information:
    ├─ Nickname: {data['basicInfo'].get('nickname', 'Not Available')}
    ├─ Account ID: {data['basicInfo'].get('accountId', 'Not Available')}
    ├─ Region: {data['basicInfo'].get('region', 'Not Available')}
    ├─ Level: {data['basicInfo'].get('level', 'Not Available')}
    ├─ Badges: {data['basicInfo'].get('badgeCnt', 'Not Available')}
    ├─ Likes: {data['basicInfo'].get('liked', 'Not Available')}
    ├─ Avatar: {data['basicInfo'].get('headPic', 'Not Available')}
    └─ Experience: {data['basicInfo'].get('exp', 'Not Available')}

    📈 Player Ranking:
    ├─ BR Ranking Points: {data['basicInfo'].get('rankingPoints', 'Not Available')}
    ├─ CS Ranking Points: {data['basicInfo'].get('csRankingPoints', 'Not Available')}
    ├─ BR Rank Visibility: {'Visible' if data['basicInfo'].get('showBrRank', False) else 'Hidden'}
    └─ CS Rank Visibility: {'Visible' if data['basicInfo'].get('showCsRank', False) else 'Hidden'}

    💬 Social Information:
    ├─ Time Active: {data['socialInfo'].get('timeActive', 'Not Available')}
    ├─ Language: {data['socialInfo'].get('language', 'Not Available')}
    └─ Signature: {data['socialInfo'].get('signature', 'Not Available')}

    👥 Clan Information:
    ├─ Clan Name: {data['clanBasicInfo'].get('clanName', 'Not Available')}
    ├─ Clan ID: {data['clanBasicInfo'].get('clanId', 'Not Available')}
    ├─ Clan Level: {data['clanBasicInfo'].get('clanLevel', 'Not Available')}
    ├─ Members Count: {data['clanBasicInfo'].get('memberNum', 'Not Available')}
    └─ Clan Leader: {data.get('captainBasicInfo', {}).get('nickname', 'Not Available')}

    🐾 Pet Information:
    ├─ Pet Name: {data['petInfo'].get('name', 'Not Available')}
    ├─ Pet Level: {data['petInfo'].get('level', 'Not Available')}
    ├─ Pet Experience: {data['petInfo'].get('exp', 'Not Available')}
    └─ Pet Skill: {data['petInfo'].get('selectedSkillId', 'Not Available')}

    └────────────────────┘
    """
    return formatted_text

# Function to create inline keyboard with developer button
def get_developer_button():
    button = InlineKeyboardButton("المطور👨‍💻", url="https://t.me/l7l7aj")  # Change with your actual link
    keyboard = InlineKeyboardMarkup([[button]])
    return keyboard

# Function to handle player info requests
async def send_info(update: Update, context):
    # Ensure the message exists
    if update.message is None:
        return

    chat_id = update.message.chat_id
    message_text = update.message.text.strip()

    # Check if the message comes from the correct group
    if update.message.chat.type == "supergroup" and update.message.chat.id == GROUP_ID:
        if message_text.startswith("l7 "):  # Check if message starts with "l7 "
            uid = message_text[3:].strip()  # Extract the ID after "l7 "
            data = get_player_data(uid)  # Get player data from API
            formatted_text = create_formatted_text(data)  # Format the player data
            
            # Send the formatted message with the "Developer" button
            image_url = 'https://h.top4top.io/p_32782fqm40.png'  # صورة تعليمية ثابتة
            await update.message.reply_photo(photo=image_url, caption=formatted_text, reply_markup=get_developer_button())
        else:
            return  # Ignore other messages in the group
    else:
        # If the message is not from the correct group, do nothing
        return

# Function to send a welcome message in private (when user types /start)
async def private_welcome(update: Update, context):
    if update.message.chat.type == "private":
        await update.message.reply_text(
            "⚠️ مرحبا بك في بوت L7 INFO FF! ⚠️\n\n"
            "🚨 يجب عليك الانضمام إلى المجموعة لاستخدام البوت.\n"
            "🔹 انضم إلى المجموعة هنا: https://t.me/l7aj_ff_group"
        )

# Function to send a welcome message when a user joins the group
async def welcome_user(update: Update, context):
    if update.message.new_chat_members:
        for new_member in update.message.new_chat_members:
            if new_member.is_bot:
                continue
            # Send a welcome message when a new user joins the group
            await update.message.reply_text(
                f"🎉 مرحباً بك في المجموعة! 🎉\n\n"
                "🌟 مرحبا بك في بوت L7 INFO FF! 🌟\n\n"
                "✉️ قم بإرسال `l7` ثم معرف 🆔️ الخاص بك 🚹🚺.\n\n"
                "🔹 مثال: `l7 987288316`\n\n"
                "-----------------------------------\n\n"
                "📩 فقط قم بإرسال `l7` ثم معرفك للحصول على معلوماتك!"
            )

# Function to send instructions when a user types /start in the group
async def start_in_group(update: Update, context):
    if update.message.chat.type == "supergroup" and update.message.chat.id == GROUP_ID:
        await update.message.reply_text(
            "⚠️ مرحبا بك في بوت L7 INFO FF! ⚠️\n\n"
            "🚨 يجب عليك الانضمام إلى المجموعة لاستخدام البوت.\n"
            "🔹 انضم إلى المجموعة هنا: https://t.me/l7_7aj"
        )

# Function to set up and run the bot
def main():
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", private_welcome))  # This sends the welcome message in private
    application.add_handler(CommandHandler("start", start_in_group))  # This sends the welcome message in the group
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_info))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_user))

    # Run the bot with polling
    application.run_polling()

# Run the bot
if __name__ == "__main__":
    main()
