#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت تست فوروارد ربات تلگرام
"""

import asyncio
from telegram_auto_forward import TelegramAutoForward

async def test_forward():
    """تست فوروارد آخرین پیام"""
    try:
        print("🧪 شروع تست فوروارد...")
        print("=" * 40)
        
        # ایجاد نمونه ربات
        bot = TelegramAutoForward()
        
        # اتصال به تلگرام
        await bot.client.start(phone=bot.phone)
        print("✅ اتصال برقرار شد")
        
        # تست فوروارد
        await bot.test_forward()
        
        # قطع اتصال
        await bot.client.disconnect()
        print("✅ تست کامل شد")
        
    except Exception as e:
        print(f"❌ خطا در تست: {e}")

async def get_channel_info():
    """دریافت اطلاعات کانال‌ها"""
    try:
        print("📊 دریافت اطلاعات کانال‌ها...")
        print("=" * 40)
        
        bot = TelegramAutoForward()
        await bot.client.start(phone=bot.phone)
        
        # اطلاعات کانال مبدا
        source_info = await bot.get_channel_info(bot.source_channel)
        if source_info:
            print(f"📥 کانال مبدا:")
            print(f"   نام: {source_info['title']}")
            print(f"   ID: {source_info['id']}")
            print(f"   اعضا: {source_info['participants_count']}")
        
        print()
        
        # اطلاعات کانال مقصد
        dest_info = await bot.get_channel_info(bot.destination_channel)
        if dest_info:
            print(f"📤 کانال مقصد:")
            print(f"   نام: {dest_info['title']}")
            print(f"   ID: {dest_info['id']}")
            print(f"   اعضا: {dest_info['participants_count']}")
        
        await bot.client.disconnect()
        
    except Exception as e:
        print(f"❌ خطا: {e}")

async def main():
    """منوی اصلی تست"""
    print("🧪 اسکریپت تست ربات اتوفوروارد")
    print("=" * 40)
    print("1. تست فوروارد آخرین پیام")
    print("2. نمایش اطلاعات کانال‌ها")
    print("3. خروج")
    
    while True:
        try:
            choice = input("\nانتخاب کنید (1-3): ").strip()
            
            if choice == "1":
                await test_forward()
                break
            elif choice == "2":
                await get_channel_info()
                break
            elif choice == "3":
                print("👋 خروج...")
                break
            else:
                print("❌ انتخاب نامعتبر")
                
        except KeyboardInterrupt:
            print("\n👋 خروج...")
            break

if __name__ == "__main__":
    asyncio.run(main())