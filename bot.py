import os
import logging
from flask import Flask, request
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import google.generativeai as genai
from dotenv import load_dotenv

# إعداد الـ Logging لرؤية ما يحدث في الـ Console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تحميل الإعدادات
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
URL = os.getenv("URL")
PORT = int(os.environ.get("PORT", 8080))

# إعداد Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# إعداد Flask
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        logger.info(f"رسالة وصلت من تليجرام: {request.json}")
        return "OK", 200
    return "البوت يعمل بنجاح!"

def run_flask():
    app.run(host='0.0.0.0', port=PORT)

# دوال البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('أهلاً بك! البوت متصل ويعمل الآن.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    response = model.generate_content(user_text)
    await update.message.reply_text(response.text)

if __name__ == '__main__':
    # 1. تشغيل سيرفر Flask
    Thread(target=run_flask).start()

    # 2. بناء التطبيق
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # 3. إضافة الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    # 4. تفعيل الـ Webhook
    webhook_url = f"{URL}/{TELEGRAM_TOKEN}"
    application.bot.set_webhook(url=webhook_url)
    
    # 5. تشغيل البوت
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TELEGRAM_TOKEN,
        webhook_url=webhook_url
    )
