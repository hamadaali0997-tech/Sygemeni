import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import google.generativeai as genai
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# إعداد Flask
app = Flask(__name__)
@app.route('/')
def index():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# إعداد Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def start(update: Update, context):
    await update.message.reply_text('أهلاً بك! أنا جاهز.')

async def handle_message(update: Update, context):
    # هذا السطر سيكتب في الـ Logs أن البوت استلم رسالة
    print(f"--- وصلتنا رسالة جديدة: {update.message.text} ---")
    
    try:
        user_text = update.message.text
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        print(f"--- خطأ: {e} ---")
        await update.message.reply_text("حدث خطأ تقني.")

if __name__ == '__main__':
    t = Thread(target=run_flask)
    t.start()
    
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("البوت يعمل الآن وينتظر الرسائل...")
    application.run_polling()
