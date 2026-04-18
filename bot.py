import os
import logging
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, MenuButtonWebApp
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.request import HTTPXRequest

# ===================================================
# 🚀 LINK SETTINGS (এখানে তোর সব লিংক পরিবর্তন করবি)
# ===================================================

# ১. ভিডিও ১ (HD) এর লিংক এখানে বসা:
VIDEO_1_HD = "https://shrinkme.click/pPKp"

# ২. ভিডিও ২ (4K) এর লিংক এখানে বসা:
VIDEO_2_4K = "https://droplink.co/x3Azu"

# ৩. 🔥 আজকের ভাইরাল ভিডিও এর লিংক এখানে বসা:
DAILY_VIRAL_VIDEO = "https://droplink.co/x3Azu"

# 📢 আমাদের অফিশিয়াল চ্যানেল ইনভাইট লিংক:
CHANNEL_URL = "https://t.me/+eOhwVR2ZXCowNDdl"

# 📱 মিনি অ্যাপ লিংক (Adsterra Ads):
MINI_APP_URL = "https://telebot-app-rwxv.onrender.com"

# ===================================================

# --- Render-এর জন্য Flask Server (বট সচল রাখার জন্য) ---
server = Flask('')

@server.route('/')
def home():
    return "বট অনলাইনে আছে এবং ডলার জেনারেট করছে! 🚀"

def run():
    port = int(os.environ.get('PORT', 8080))
    server.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# .env ফাইল থেকে টোকেন লোড করা
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# লগিং সেটআপ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

# /start কমান্ড হ্যান্ডলার
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    
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
    
    # বাটন গ্রিড (উপরে যে লিংকগুলো সেট করেছিস সেগুলো এখানে কাজ করবে)
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

# বাটন ক্লিক হ্যান্ডলার
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
            "অ্যাড পেজটি আসার পর কয়েক সেকেন্ড অপেক্ষা করে 'Continue' বা 'Get Link' বাটনে ক্লিক করুন।"
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

    # কমান্ড এবং বাটন হ্যান্ডলার সেটআপ
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("--- বট এখন ক্লিন এবং অর্গানাইজড মোডে চালু আছে ---")
    
    # পুরনো আপডেট ড্রপ করে পোলিং শুরু করা (যাতে ডাবল মেসেজ না আসে)
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
