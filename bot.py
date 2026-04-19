import os
import logging
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
from pymongo import MongoClient  # MongoDB লাইব্রেরি যোগ করা হয়েছে
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, MenuButtonWebApp
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.request import HTTPXRequest

# ===================================================
# 🚀 LINK & ADMIN SETTINGS (তোর দেওয়া সব লিংক এখানে আছে)
# ===================================================

# তোর নিজের টেলিগ্রাম আইডি (অ্যাডমিন প্যানেল এক্সেস করার জন্য)
ADMIN_ID = 7657544184 

# ১. ভিডিও ১ (HD) এর লিংক:
VIDEO_1_HD = "https://shrinkme.click/pPKp"

# ২. ভিডিও ২ (4K) এর লিংক:
VIDEO_2_4K = "https://droplink.co/x3Azu"

# ৩. 🔥 আজকের ভাইরাল ভিডিও এর লিংক:
DAILY_VIRAL_VIDEO = "https://droplink.co/x3Azu"

# 📢 আমাদের অফিশিয়াল চ্যানেল ইনভাইট লিংক:
CHANNEL_URL = "https://t.me/+eOhwVR2ZXCowNDdl"

# 📱 মিনি অ্যাপ লিংক (Adsterra Ads):
MINI_APP_URL = "https://telebot-app-rwxv.onrender.com"

# ===================================================
# 🗄️ DATABASE SETTINGS (MongoDB)
# ===================================================
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

# MongoDB কানেকশন সেটআপ
client = MongoClient(MONGO_URI)
db = client['viral_bot_db']
users_collection = db['users']
# ===================================================

# --- Render-এর জন্য Flask Server ---
server = Flask('')

@server.route('/')
def home():
    return "বট অনলাইনে আছে এবং ডাটাবেস কানেক্টেড! 🚀"

def run():
    port = int(os.environ.get('PORT', 8080))
    server.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# লগিং সেটআপ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

# --- ইউজার আইডি সেভ করার ফাংশন (MongoDB ভার্সন) ---
def save_user(user_id, first_name):
    # ইউজার যদি আগে থেকে না থাকে তবেই নতুন করে সেভ হবে
    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id, "first_name": first_name}},
        upsert=True
    )

# --- /start কমান্ড হ্যান্ডলার ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ব্রডকাস্টের জন্য ইউজার আইডি ডাটাবেসে সেভ করা হচ্ছে
    user = update.effective_user
    save_user(user.id, user.first_name)
    
    user_name = user.first_name
    
    # ১. বাম পাশের নিচে 'Watch Video' মেনু বাটন সেট করা
    await context.bot.set_chat_menu_button(
        chat_id=update.effective_chat.id,
        menu_button=MenuButtonWebApp(
            text="Watch Video 🔞",
            web_app=WebAppInfo(url=MINI_APP_URL)
        )
    )

    # ২. প্রিমিয়াম স্বাগত মেসেজ
    welcome_text = (
        f"✨ *স্বাগতম, {user_name}!* ✨\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📥 *ভাইরাল ভিডিও ডাউনলোড সেন্টার*\n\n"
        "নিচের বাটন থেকে আপনার পছন্দের ভিডিও\n"
        "সিলেক্ট করে লিংক সংগ্রহ করুন।\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 *নির্দেশনা:* ভিডিওটি দেখতে নিচের বাটনগুলো\n"
        "ব্যবহার করুন। সেরা অভিজ্ঞতার জন্য নিচের\n"
        "বামের 'Watch Video' বাটনে ক্লিক করুন।"
    )
    
    # বাটন গ্রিড
    keyboard = [
        [
            InlineKeyboardButton("🎬 ভিডিও ১ (HD)", callback_data='video_1'),
            InlineKeyboardButton("🎬 ভিডিও ২ (4K)", callback_data='video_2')
        ],
        [InlineKeyboardButton("🔥 আজকের ভাইরাল ভিডিও", callback_data='video_3')],
        [InlineKeyboardButton("📢 আমাদের অফিশিয়াল চ্যানেল", url=CHANNEL_URL)] 
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text, 
        reply_markup=reply_markup, 
        parse_mode='Markdown'
    )

# --- ব্রডকাস্ট কমান্ড (MongoDB থেকে আইডি নিয়ে) ---
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # অ্যাডমিন ভেরিফিকেশন
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ দুঃখিত, এই কমান্ডটি শুধুমাত্র অ্যাডমিনের জন্য।")
        return

    if not context.args:
        await update.message.reply_text("⚠️ মেসেজটি লিখুন। উদাহরণ: `/broadcast আজ নতুন ভিডিও আসছে!`")
        return

    message_to_send = " ".join(context.args)
    
    # ডাটাবেস থেকে সব ইউজার খুঁজে বের করা
    all_users = list(users_collection.find({}))
    
    if not all_users:
        await update.message.reply_text("❌ কোনো ইউজার খুঁজে পাওয়া যায়নি!")
        return

    success = 0
    fail = 0
    
    status_msg = await update.message.reply_text(f"📢 {len(all_users)} জন ইউজারের কাছে পাঠানো শুরু হচ্ছে...")

    for user_doc in all_users:
        try:
            await context.bot.send_message(
                chat_id=user_doc['user_id'], 
                text=f"📢 *অফিশিয়াল ঘোষণা:*\n\n{message_to_send}", 
                parse_mode='Markdown'
            )
            success += 1
        except Exception:
            fail += 1

    await status_msg.edit_text(f"✅ পাঠানো শেষ!\n🎯 সফল: {success}\n❌ ব্যর্থ: {fail} (বট ব্লক করেছে)")

# --- বাটন ক্লিক হ্যান্ডলার ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # ডাটা অনুযায়ী সঠিক লিংকটি বেছে নেওয়া
    links = {
        'video_1': VIDEO_1_HD,
        'video_2': VIDEO_2_4K,
        'video_3': DAILY_VIRAL_VIDEO 
    }

    selected_link = links.get(query.data)
    
    if selected_link:
        keyboard = [[InlineKeyboardButton("🌐 ভিডিওটি ওপেন করুন", url=selected_link)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        response_text = (
            "✅ *আপনার ভিডিও লিংকটি রেডি!*\n\n"
            "💡 *নির্দেশনা:* ভিডিওটি দেখতে নিচের বাটনে ক্লিক করুন। "
            "অ্যাড পেজটি আসার পর কয়েক সেকেন্ড অপেক্ষা করে 'Continue' বা 'Get Link' বাটনে ক্লিক করুন।"
        )
        
        await query.message.reply_text(
            response_text, 
            reply_markup=reply_markup, 
            parse_mode='Markdown'
        )

def main():
    # ডামি সার্ভার চালু রাখা
    keep_alive()

    # টাইম-আউট কনফিগারেশন
    request_config = HTTPXRequest(
        connect_timeout=40, 
        read_timeout=40
    )

    app = (
        Application.builder()
        .token(TOKEN)
        .request(request_config)
        .build()
    )

    # হ্যান্ডলার সেটআপ
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast)) # ব্রডকাস্ট যোগ করা হয়েছে
    app.add_handler(CallbackQueryHandler(button_handler))

    print("--- বট এখন অ্যাডমিন প্যানেল এবং MongoDB মোডে চালু আছে ---")
    
    # পোলিং শুরু
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
