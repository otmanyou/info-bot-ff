import requests
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Bot Token
TOKEN = os.getenv("TOKEN")

# ID الخاص بالمدير والمجموعة
ADMIN_ID = int(os.getenv("ADMIN_ID"))  # تأكد من تحويل القيمة إلى رقم

GROUP_ID = int(os.getenv("GROUP_ID"))

# روابط الملفات
ITEMS_URL = "https://raw.githubusercontent.com/TH-HACK/l7aj-Items/refs/heads/main/itemData.json"
LIST_URL = "https://raw.githubusercontent.com/jinix6/ff-resources/refs/heads/main/pngs/300x300/list.json"
BASE_IMAGE_URL = "https://raw.githubusercontent.com/jinix6/ff-resources/refs/heads/main/pngs/300x300/"

# دالة لتنسيق الوقت
def format_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %I:%M %p") if timestamp else "Not Available"

# دالة لجلب بيانات اللاعب من API
def get_player_data(uid):
    url = f"https://fox-api-lyart.vercel.app/info?id={uid}"
    r = requests.get(url)
    return r.json()

# دالة لتنسيق النصوص
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

# دالة للبحث عن icon باستخدام Avatar ID
def get_icon_from_avatar(avatar_id):
    try:
        items_data = requests.get(ITEMS_URL).json()
        for item in items_data:
            if item["itemID"] == avatar_id:
                return item.get("icon")
    except Exception as e:
        print(f"Error fetching item data: {e}")
    return None

# دالة لإنشاء رابط الصورة النهائية
def get_image_url(icon_name):
    try:
        list_data = requests.get(LIST_URL).json()
        for item in list_data:
            if icon_name in item:
                return BASE_IMAGE_URL + item
    except Exception as e:
        print(f"Error fetching image list: {e}")
    return None

# دالة لإرسال المعلومات والصورة
async def send_info(update: Update, context):
    if update.message is None:
        return

    message_text = update.message.text.strip()
    if update.message.chat.type == "supergroup" and update.message.chat.id == GROUP_ID:
        if message_text.startswith("l7 "):
            uid = message_text[3:].strip()
            data = get_player_data(uid)
            avatar_id = data['basicInfo'].get('headPic', 'Not Available')
            
            icon_name = get_icon_from_avatar(avatar_id)
            image_url = get_image_url(icon_name) if icon_name else None
            
            if image_url:
                formatted_text = create_formatted_text(data)
                await update.message.reply_photo(photo=image_url, caption=formatted_text)
            else:
                formatted_text = create_formatted_text(data)
                await update.message.reply_text(formatted_text)

# دالة الترحيب في الخاص
async def private_welcome(update: Update, context):
    if update.message.chat.type == "private":
        await update.message.reply_text(
            "⚠️ مرحبا بك في بوت L7 INFO FF! ⚠️\n\n"
            "🚨 يجب عليك الانضمام إلى المجموعة لاستخدام البوت.\n"
            "🔹 انضم إلى المجموعة هنا: https://t.me/l7_7aj"
        )

# دالة ترحيب عند الانضمام للمجموعة
async def welcome_user(update: Update, context):
    if update.message.new_chat_members:
        for new_member in update.message.new_chat_members:
            if not new_member.is_bot:
                await update.message.reply_text(
                    f"🎉 مرحباً بك في المجموعة! 🎉\n\n"
                    "🌟 قم بإرسال `l7` ثم معرفك للحصول على معلوماتك!"
                )

# إعداد البوت
def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", private_welcome))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_info))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_user))
    application.run_polling()

if __name__ == "__main__":
    main()
