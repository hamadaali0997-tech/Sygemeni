import os
import logging
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# إعداد Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# إعداد Flask (للحفاظ على السيرفر يعمل)
app = Flask(__name__)
@app.route('/')
def index():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# دالات البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('أهلاً بك! أنا جاهز للرد.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    response = model.generate_content(user_text)
    await update.message.reply_text(response.text)

if __name__ == '__main__':
    # تشغيل Flask في خلفية
    t = Thread(target=run_flask)
    t.start()

    # إعداد البوت
    application = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("البوت يعمل الآن!")
    application.run_polling()
