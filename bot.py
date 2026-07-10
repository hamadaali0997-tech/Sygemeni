import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from dotenv import load_dotenv

# إعداد الـ Logging لمتابعة الأخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# تحميل الإعدادات
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# إعداد Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# دالة المحادثة (Gemini)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("عذراً، حدث خطأ أثناء المعالجة.")
        logging.error(f"Error: {e}")

# دالة الرسم (Pollinations)
async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("أرجوك اكتب وصفاً للصورة بعد الأمر /draw\nمثال: /draw a cute cat")
        return
        
    await update.message.reply_text("جاري رسم الصورة، لحظة من فضلك...")
    
    # بناء رابط الصورة الذكي
    safe_prompt = prompt.replace(" ", "%20")
    image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&nologo=true"
    
    try:
        await update.message.reply_photo(photo=image_url)
    except Exception as e:
        await update.message.reply_text("فشل في تحميل الصورة، جرب وصفاً آخر.")
        logging.error(f"Image Error: {e}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # الأوامر
    application.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("أهلاً! أنا بوت Gemini، يمكنني المحادثة ورسم الصور.\n- اكتب أي شيء للمحادثة.\n- استخدم /draw لرسم صورة.")))
    application.add_handler(CommandHandler("draw", generate_image))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("البوت يعمل الآن بنظام Polling (رسم + محادثة)...")
    application.run_polling()
