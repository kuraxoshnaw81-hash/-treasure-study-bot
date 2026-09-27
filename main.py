import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "سڵاو! من یارمەتیدەری زیرەکی خوێندنەکاتم.\n\n"
        "دەتوانیت هەر دەقێک، پرسیارێک، یان وێنەی پەڕتووکم بۆ بنێریت تاوەکو:\n"
        "1. پوختەی بکەمەوە.\n"
        "2. پرسیار و وەڵامی لێ دروست بکەم.\n"
        "3. بابەتی قورست بۆ شیکار بکەم."
    )
    await update.message.reply_text(welcome_text)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text("چاوەڕێ بڕێک... سەرقاڵی شیکردنەوەی دەقەکەم ⏳")
    
    try:
        prompt = f"تکایە ئەم دەقە شیبکەرەوە و بە زمانی کوردی پوختەی بکەرەوە و خاڵە گرنگەکانی دەربهێنە:\n\n{user_text}"
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("ببوورە، کێشەیەک ڕوویدا لە شیکردنەوەی دەقەکەدا.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("وێنەکەم پێگەیشت، سەرقاڵی خوێندنەوەی دەقی ناو وێنەکەم... 📸")
    
    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        
        image_part = {
            "mime_type": "image/jpeg",
            "data": bytes(photo_bytes)
        }
        
        prompt = "ئەم وێنەیە بخوێنەوە. ئەگەر دەقی تێدایە، پوختەی بکەرەوە و ۳ پرسیار و وەڵامی کورت لەسەر بابەتەکە بە زمانی کوردی دروست بکە."
        response = model.generate_content([prompt, image_part])
        
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("ببوورە، نەمتوانی دەقی ناو وێنەکە بە ڕوونی بخوێنمەوە.")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("بۆتەکە بە سەرکەوتوویی دەستی بەکارکرد...")
    app.run_polling()

if __name__ == '__main__':
    main()
