#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت راه‌اندازی ربات اتوفوروارد تلگرام
"""

import os
import shutil
import asyncio
from telegram_auto_forward import TelegramAutoForward

def setup_environment():
    """راه‌اندازی محیط کار"""
    print("🔧 راه‌اندازی محیط کار...")
    
    # ایجاد فایل .env اگر وجود ندارد
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            shutil.copy('.env.example', '.env')
            print("✅ فایل .env از .env.example کپی شد")
            print("⚠️  لطفاً فایل .env را ویرایش کنید و تنظیمات خود را وارد کنید")
        else:
            print("❌ فایل .env.example یافت نشد")
    else:
        print("✅ فایل .env موجود است")

def check_requirements():
    """بررسی کتابخانه‌های مورد نیاز"""
    try:
        import telethon
        import dotenv
        print("✅ تمام کتابخانه‌های مورد نیاز نصب شده‌اند")
        return True
    except ImportError as e:
        print(f"❌ کتابخانه مورد نیاز نصب نیست: {e}")
        print("برای نصب دستور زیر را اجرا کنید:")
        print("pip install -r requirements.txt")
        return False

async def test_connection():
    """تست اتصال و تنظیمات"""
    try:
        print("🔍 تست اتصال...")
        bot = TelegramAutoForward()
        
        # اتصال به تلگرام
        await bot.client.start(phone=bot.phone)
        print("✅ اتصال به تلگرام برقرار شد")
        
        # تست دسترسی به کانال‌ها
        await bot._check_channels()
        
        # دریافت اطلاعات کانال‌ها
        source_info = await bot.get_channel_info(bot.source_channel)
        dest_info = await bot.get_channel_info(bot.destination_channel)
        
        if source_info:
            print(f"📥 کانال مبدا: {source_info['title']}")
        
        if dest_info:
            print(f"📤 کانال مقصد: {dest_info['title']}")
        
        await bot.client.disconnect()
        print("✅ تست اتصال موفقیت‌آمیز بود")
        return True
        
    except Exception as e:
        print(f"❌ خطا در تست اتصال: {e}")
        return False

async def main():
    """تابع اصلی setup"""
    print("🤖 راه‌اندازی ربات اتوفوروارد تلگرام")
    print("=" * 50)
    
    # راه‌اندازی محیط
    setup_environment()
    
    # بررسی کتابخانه‌ها
    if not check_requirements():
        return
    
    # تست اتصال
    if not os.path.exists('.env'):
        print("⚠️  ابتدا فایل .env را تنظیم کنید")
        return
    
    # تایید برای تست
    test = input("\n🔍 آیا می‌خواهید اتصال را تست کنید؟ (y/n): ")
    if test.lower() in ['y', 'yes', 'بله']:
        success = await test_connection()
        if success:
            print("\n🎉 ربات آماده استفاده است!")
            print("برای اجرا دستور زیر را وارد کنید:")
            print("python telegram_auto_forward.py")

if __name__ == "__main__":
    asyncio.run(main())