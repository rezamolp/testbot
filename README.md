# 🤖 ربات اتوفوروارد تلگرام

یک ربات پایتون برای فوروارد خودکار پست‌های کانال‌های تلگرام

## ✨ ویژگی‌ها

- 🔄 فوروارد خودکار پیام‌های جدید از کانال مبدا به مقصد
- 📱 پشتیبانی از تمام انواع پیام (متن، عکس، ویدیو، فایل، صوت و...)
- ⏱️ قابلیت تنظیم تاخیر بین فوروارد پیام‌ها
- 📝 سیستم لاگ کامل
- 🔧 تنظیمات آسان از طریق فایل .env
- 🛡️ مدیریت خطا و بازیابی خودکار

## 📋 پیش‌نیازها

- Python 3.7 یا بالاتر
- اکانت تلگرام
- API Key از my.telegram.org
- دسترسی ادمین به کانال مقصد

## 🚀 نصب و راه‌اندازی

### 1️⃣ دانلود پروژه
```bash
git clone <repository-url>
cd telegram-auto-forward
```

### 2️⃣ نصب کتابخانه‌ها
```bash
pip install -r requirements.txt
```

### 3️⃣ دریافت API Key
1. به https://my.telegram.org وارد شوید
2. `API ID` و `API Hash` خود را کپی کنید

### 4️⃣ تنظیم فایل .env
```bash
cp .env.example .env
```

فایل `.env` را ویرایش کنید:
```env
# تنظیمات API تلگرام
API_ID=12345678
API_HASH=your_api_hash_here
PHONE_NUMBER=+98xxxxxxxxxx

# کانال مبدا (منبع)
SOURCE_CHANNEL=@source_channel_username

# کانال مقصد 
DESTINATION_CHANNEL=@destination_channel_username

# تاخیر بین فوروارد (ثانیه) - اختیاری
FORWARD_DELAY=5
```

### 5️⃣ اجرای اسکریپت راه‌اندازی
```bash
python setup.py
```

### 6️⃣ اجرای ربات
```bash
python telegram_auto_forward.py
```

## ⚙️ تنظیمات

### متغیرهای محیط (.env)

| متغیر | توضیحات | مثال |
|-------|---------|-------|
| `API_ID` | شناسه API از my.telegram.org | `12345678` |
| `API_HASH` | هش API از my.telegram.org | `abcd1234...` |
| `PHONE_NUMBER` | شماره تلفن با کد کشور | `+989123456789` |
| `SOURCE_CHANNEL` | کانال مبدا (منبع) | `@mychannel` |
| `DESTINATION_CHANNEL` | کانال مقصد | `@targetchannel` |
| `FORWARD_DELAY` | تاخیر بین فوروارد (ثانیه) | `5` |

### نکات مهم

- شماره تلفن باید با کد کشور (+98 برای ایران) باشد
- نام کانال‌ها باید با @ شروع شوند
- ربات باید به هر دو کانال دسترسی داشته باشد
- برای کانال مقصد باید دسترسی ادمین داشته باشید

## 📁 ساختار فایل‌ها

```
telegram-auto-forward/
├── telegram_auto_forward.py    # فایل اصلی ربات
├── setup.py                   # اسکریپت راه‌اندازی
├── requirements.txt           # کتابخانه‌های مورد نیاز
├── .env.example              # نمونه فایل تنظیمات
├── .env                      # فایل تنظیمات (ایجاد می‌شود)
├── auto_forward.log          # فایل لاگ (ایجاد می‌شود)
├── auto_forward_session.session # فایل session تلگرام (ایجاد می‌شود)
└── README.md                 # راهنمای استفاده
```

## 🎛️ نحوه استفاده

### اجرای معمولی
```bash
python telegram_auto_forward.py
```

### اجرا در Background (Linux/Mac)
```bash
nohup python telegram_auto_forward.py &
```

### متوقف کردن ربات
- `Ctrl + C` در ترمینال
- یا کشتن پروسه در حالت background

## 📊 مثال لاگ

```
2024-01-15 10:30:15 - __main__ - INFO - ربات اتوفوروارد مقداردهی شد
2024-01-15 10:30:15 - __main__ - INFO - کانال مبدا: @source_channel
2024-01-15 10:30:15 - __main__ - INFO - کانال مقصد: @dest_channel
2024-01-15 10:30:16 - __main__ - INFO - اتصال به تلگرام برقرار شد
2024-01-15 10:30:17 - __main__ - INFO - دسترسی به کانال مبدا تایید شد: My Source Channel
2024-01-15 10:30:18 - __main__ - INFO - دسترسی به کانال مقصد تایید شد: My Destination Channel
2024-01-15 10:30:19 - __main__ - INFO - ربات شروع به کار کرد - منتظر پیام‌های جدید...
2024-01-15 10:35:22 - __main__ - INFO - پیام جدید دریافت شد از @source_channel
2024-01-15 10:35:22 - __main__ - INFO - نوع پیام: متن
2024-01-15 10:35:27 - __main__ - INFO - پیام با موفقیت فوروارد شد به @dest_channel
```

## 🔧 عیب‌یابی

### خطاهای رایج

1. **خطای احراز هویت**
   ```
   AuthKeyError: The authorization key is invalid
   ```
   **راه‌حل:** فایل session را پاک کنید و دوباره اجرا کنید

2. **خطای دسترسی به کانال**
   ```
   ChannelPrivateError: The channel specified is private
   ```
   **راه‌حل:** بررسی کنید که ربات به کانال دسترسی دارد

3. **خطای فوروارد**
   ```
   ChatAdminRequiredError: Admin privileges are required
   ```
   **راه‌حل:** ربات باید ادمین کانال مقصد باشد

### نکات عیب‌یابی

- فایل‌های log را بررسی کنید
- تنظیمات .env را دوباره چک کنید
- اتصال اینترنت را بررسی کنید
- محدودیت‌های API تلگرام را در نظر بگیرید

## 🛡️ امنیت

- فایل `.env` را در git ignore قرار دهید
- API keys را با کسی به اشتراک نگذارید
- از VPN استفاده کنید اگر در کشورتان تلگرام فیلتر است

## 📜 مجوز

این پروژه تحت مجوز MIT منتشر شده است.

## 🤝 مشارکت

برای مشارکت در این پروژه:
1. Fork کنید
2. Branch جدید ایجاد کنید
3. تغییرات خود را commit کنید
4. Pull Request ارسال کنید

## 📞 پشتیبانی

اگر با مشکلی مواجه شدید، یک Issue در GitHub ایجاد کنید.

---
💡 **نکته:** این ربات فقط برای اهداف قانونی و اخلاقی استفاده شود.