import os
import logging
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, MenuButtonWebApp
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.request import HTTPXRequest

# --- Render-এর জন্য Flask Server (যাতে বট অফ না হয়) ---
server = Flask('')

@server.route('/')
def home():
    return "বট এখন অনলাইনে আছে! 🚀"

def run():
    # Render সাধারণত পোর্ট ৮০৮০ বা ৫০০০ ব্যবহার করে, তবে ০.০.০.০ দেওয়া জরুরি
    server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()
# ---------------------------------------------------

# .env ফাইল থেকে টোকেন লোড করা
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# লগিং সেটআপ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

# তোর হোস্টিং করা মিনি অ্যাপের লিংক এখানে দিবি
# (ধাপ ১ এ Render Static Site থেকে যে লিংকটা পেয়েছিস)
MINI_APP_URL = "https://telebot-app-rwxv.onrender.com"

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
    
    # বাটন গ্রিড (পাশাপাশি সাজানো)
    keyboard = [
        [
            InlineKeyboardButton("🎬 ভিডিও ১ (HD)", callback_data='video_1'),
            InlineKeyboardButton("🎬 ভিডিও ২ (4K)", callback_data='video_2')
        ],
        [InlineKeyboardButton("🔥 আজকের ভাইরাল ভিডিও", callback_data='video_3')],
        [InlineKeyboardButton("📢 আমাদের অফিশিয়াল চ্যানেল", url='https://t.me/your_channel_username')]
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

    # এখানে তোর মনিটাইজ করা শর্টনার লিংকগুলো দিবি
    links = {
        'video_1': "https://shorlink.com/v1",
        'video_2': "https://shorlink.com/v2",
        'video_3': "https://shorlink.com/v3"
    }

    selected_link = links.get(query.data)
    
    if selected_link:
        # সরাসরি ওপেন করার জন্য ইনলাইন বাটন
        keyboard = [[InlineKeyboardButton("🌐 ভিডিওটি ওপেন করুন", url=selected_link)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        response_text = (
            "✅ *আপনার লিংকটি তৈরি হয়ে গেছে!*\n\n"
            f"🔗 *ভিডিও লিংক:* {selected_link}\n\n"
            "💡 *নির্দেশনা:* সরাসরি দেখতে নিচের বাটনে ক্লিক করুন।"
        )
        
        await query.message.reply_text(
            response_text, 
            reply_markup=reply_markup, 
            parse_mode='Markdown',
            disable_web_page_preview=False
        )

def main():
    # Render-এর জন্য ডামি সার্ভার চালু করা
    keep_alive()

    # টাইম-আউট সেটিংস
    request_config = HTTPXRequest(
        connect_timeout=40, 
        read_timeout=40
    )

    # বট অ্যাপ্লিকেশন বিল্ড
    app = (
        Application.builder()
        .token(TOKEN)
        .request(request_config)
        .build()
    )

    # হ্যান্ডলার অ্যাড করা
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("--- বট এখন ফুল প্রিমিয়াম মোডে চালু আছে ---")
    
    # বট রান করা
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
