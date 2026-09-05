FROM python:3.10-slim

# تثبيت FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# إنشاء مجلد العمل
WORKDIR /app

# نسخ ملفات المتطلبات
COPY requirements.txt .

# تنصيب المكتبات
RUN pip install --no-cache-dir -r requirements.txt

# نسخ الكود
COPY bot.py .

# إنشاء مجلد للتحميلات
RUN mkdir -p downloads

# أمر التشغيل
CMD ["python", "bot.py"]
