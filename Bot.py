import os
import re
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import yt_dlp

# ===================== الإعدادات الأساسية =====================
TOKEN = "8203080422:AAFYxonm0YHcrK6k3IDGcrkbrvAt3xBCGEg"
DOWNLOAD_PATH = "downloads"
MAX_FILE_SIZE = 50 * 1024 * 1024

if not os.path.exists(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===================== دوال التحميل =====================
def get_video_info(url):
    ydl_opts = {'quiet': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'بدون عنوان'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'مجهول'),
            }
        except:
            return None

def download_media(url, media_type='video'):
    if media_type == 'video':
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_PATH}/%(title)s.%(ext)s',
            'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
        }
    else:
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_PATH}/%(title)s.%(ext)s',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if media_type == 'audio':
                filename = filename.rsplit('.', 1)[0] + '.mp3'
            
            if os.path.exists(filename):
                if os.path.getsize(filename) > MAX_FILE_SIZE:
                    os.remove(filename)
                    return None, "⚠️ الملف أكبر من 50 ميجا"
                return filename, None
            return None, "❌ فشل التحميل"
    except Exception as e:
        return None, f"❌ خطأ: {str(e)[:100]}"

# ===================== أوامر البوت =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    first_name = user.first_name if user.first_name else "صديقي"
    
    keyboard = [
        [InlineKeyboardButton("📹 تحميل فيديو", callback_data='video')],
        [InlineKeyboardButton("🎵 تحميل صوت فقط", callback_data='audio')],
        [InlineKeyboardButton("❓ مساعدة", callback_data='help')]
    ]
    
    await update.message.reply_text(
        f"🎬 **مرحباً بك {first_name}!**\n\n"
        "أنا بوت لتحميل الفيديوهات من:\n"
        "• يوتيوب 📺\n• انستجرام 📸\n• فيسبوك 📘\n• تيك توك 🎵\n\n"
        "**الأوامر المتاحة:**\n"
        "/video [الرابط] - تحميل فيديو\n"
        "/audio [الرابط] - تحميل الصوت فقط\n"
        "/help - عرض المساعدة",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 **دليل الاستخدام:**\n\n"
        "1️⃣ تحميل فيديو:\n"
        "`/video https://youtube.com/watch?v=...`\n\n"
        "2️⃣ تحميل صوت فقط:\n"
        "`/audio https://youtube.com/watch?v=...`\n\n"
        "🌐 المنصات المدعومة:\n"
        "YouTube • Instagram • Facebook • TikTok",
        parse_mode='Markdown'
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ أرسل الرابط بعد الأمر:\n`/video [الرابط]`", parse_mode='Markdown')
        return
    await process_download(update, context.args[0], 'video')

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ أرسل الرابط بعد الأمر:\n`/audio [الرابط]`", parse_mode='Markdown')
        return
    await process_download(update, context.args[0], 'audio')

async def process_download(update: Update, url: str, media_type: str):
    msg = await update.message.reply_text("⏳ جاري التحميل...")
    
    info = get_video_info(url)
    if not info:
        await msg.edit_text("❌ الرابط غير صحيح أو غير مدعوم!")
        return
    
    filename, error = download_media(url, media_type)
    if error:
        await msg.edit_text(f"❌ {error}")
        return
    
    await msg.edit_text("📤 جاري الرفع إلى تليجرام...")
    
    try:
        with open(filename, 'rb') as file:
            if media_type == 'video':
                await update.message.reply_video(video=file, caption=f"🎬 {info['title'][:50]}")
            else:
                await update.message.reply_audio(audio=file, title=info['title'][:50])
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ خطأ في الرفع: {str(e)[:100]}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'video':
        await query.edit_message_text("📹 أرسل رابط الفيديو الآن:")
        context.user_data['action'] = 'video'
    elif query.data == 'audio':
        await query.edit_message_text("🎵 أرسل رابط الفيديو لاستخراج الصوت:")
        context.user_data['action'] = 'audio'
    elif query.data == 'help':
        await help_command(update, context)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'action' not in context.user_data:
        return
    
    url = update.message.text
    if not re.match(r'^https?://(www\.)?(youtube|instagram|facebook|tiktok)\.[a-z]{2,}/', url):
        await update.message.reply_text("❌ الرجاء إرسال رابط صحيح")
        return
    
    action = context.user_data['action']
    await process_download(update, url, action)
    del context.user_data['action']

# ===================== التشغيل =====================
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("video", handle_video))
    app.add_handler(CommandHandler("audio", handle_audio))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("🚀 البوت شغال...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
