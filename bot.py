import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# هذا الرابط هو رابط مشروعك على Render
URL = "https://sygemeni.onrender.com" 

# إعداد Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# إعداد Flask و Telegram
app = Flask(__name__)
bot = Bot(token=TELEGRAM_TOKEN)
# إعداد Dispatcher (نستخدم مكتبة python-telegram-bot القديمة المتوافقة مع Webhook بسهولة)
dispatcher = Dispatcher(bot, None, workers=0)

def start(update, context):
    update.message.reply_text('أهلاً بك! أنا جاهز للرد عبر Webhook.')

def handle_message(update, context):
    user_text = update.message.text
    response = model.generate_content(user_text)
    update.message.reply_text(response.text)

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    dispatcher.process_
