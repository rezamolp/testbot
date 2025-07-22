#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تولید داده‌های نمونه برای تست سیستم آمارگیری
Generate Sample Data for Statistics Testing
"""

import random
from datetime import datetime, timedelta
from statistics import StatisticsDB, MessageStats
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_sample_data(days=30, messages_per_day_range=(10, 100)):
    """تولید داده‌های نمونه برای آمارگیری"""
    
    stats_db = StatisticsDB()
    
    # انواع پیام
    message_types = ['متن', 'عکس', 'ویدیو', 'فایل', 'صوت', 'پیام صوتی', 'استیکر']
    
    # کانال‌های نمونه
    source_channels = ['@tech_news', '@daily_quotes', '@funny_memes']
    dest_channels = ['@my_channel', '@backup_channel']
    
    # انواع خطا
    error_messages = [
        'ChatAdminRequiredError: Admin privileges are required',
        'ChannelPrivateError: The channel specified is private',
        'FloodWaitError: Too many requests',
        'MessageNotModifiedError: The message was not modified',
        None, None, None, None, None  # بیشتر پیام‌ها موفق هستند
    ]
    
    total_generated = 0
    
    logger.info(f"شروع تولید داده‌های نمونه برای {days} روز...")
    
    for day in range(days):
        # تاریخ
        current_date = datetime.now() - timedelta(days=days-day)
        
        # تعداد پیام‌های آن روز
        messages_count = random.randint(*messages_per_day_range)
        
        for msg in range(messages_count):
            # زمان تصادفی در آن روز
            random_hour = random.randint(0, 23)
            random_minute = random.randint(0, 59)
            random_second = random.randint(0, 59)
            
            timestamp = current_date.replace(
                hour=random_hour, 
                minute=random_minute, 
                second=random_second
            )
            
            # انتخاب تصادفی مشخصات پیام
            message_type = random.choice(message_types)
            source_channel = random.choice(source_channels)
            dest_channel = random.choice(dest_channels)
            error_msg = random.choice(error_messages)
            success = error_msg is None
            
            # تاخیر تصادفی
            forward_delay = random.uniform(0.5, 10.0)
            
            # اندازه پیام
            if message_type == 'متن':
                message_size = random.randint(10, 1000)
                has_media = False
                media_type = None
            else:
                message_size = random.randint(1000, 50000000)  # 1KB تا 50MB
                has_media = True
                media_type = message_type.lower()
            
            # ایجاد آمار
            stat = MessageStats(
                id=random.randint(1000, 999999),
                message_type=message_type,
                source_channel=source_channel,
                destination_channel=dest_channel,
                timestamp=timestamp,
                forward_delay=forward_delay,
                success=success,
                error_message=error_msg,
                message_size=message_size,
                has_media=has_media,
                media_type=media_type
            )
            
            # ثبت در پایگاه داده
            stats_db.add_message_stat(stat)
            total_generated += 1
    
    logger.info(f"✅ {total_generated:,} رکورد نمونه تولید شد")
    return total_generated

def show_generated_stats():
    """نمایش آمار تولید شده"""
    from statistics import StatisticsAnalyzer, StatisticsReporter
    
    stats_db = StatisticsDB()
    analyzer = StatisticsAnalyzer(stats_db)
    reporter = StatisticsReporter(stats_db, analyzer)
    
    print("\n📊 آمار تولید شده:")
    print("=" * 50)
    
    # آمار کلی
    metrics = analyzer.get_performance_metrics(30)
    if metrics:
        print(f"📈 کل پیام‌ها: {metrics['total_messages']:,}")
        print(f"✅ پیام‌های موفق: {metrics['successful_forwards']:,}")
        print(f"❌ پیام‌های ناموفق: {metrics['failed_forwards']:,}")
        print(f"📊 نرخ موفقیت: {metrics['success_rate']}%")
        print(f"📅 میانگین روزانه: {metrics['avg_messages_per_day']:.1f}")
    
    # انواع پیام
    message_types = stats_db.get_message_type_stats(30)
    if message_types:
        print(f"\n📱 انواع پیام:")
        for msg_type, count in sorted(message_types.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {msg_type}: {count:,}")
    
    # ساعات پیک
    peak_data = analyzer.get_peak_hours(30)
    if peak_data:
        print(f"\n🕐 ساعت پیک: {peak_data['peak_hour']}:00")
        print(f"   تعداد پیام: {peak_data['peak_hour_count']:,}")
    
    # الگوی هفتگی
    weekly_data = analyzer.get_weekly_pattern(30)
    if weekly_data:
        print(f"\n📅 پرترافیک‌ترین روز: {weekly_data['busiest_day']}")
        print(f"   تعداد پیام: {weekly_data['busiest_day_count']:,}")

def clear_all_data():
    """پاک کردن تمام داده‌ها"""
    import os
    
    try:
        if os.path.exists('forward_stats.db'):
            os.remove('forward_stats.db')
            logger.info("✅ تمام داده‌های قبلی پاک شد")
        else:
            logger.info("ℹ️ هیچ داده‌ای برای پاک کردن وجود ندارد")
    except Exception as e:
        logger.error(f"خطا در پاک کردن داده‌ها: {e}")

def main():
    """تابع اصلی"""
    print("🔧 تولید داده‌های نمونه برای آمارگیری")
    print("=" * 50)
    print("1. تولید داده‌های نمونه")
    print("2. نمایش آمار موجود")
    print("3. پاک کردن تمام داده‌ها")
    print("4. تولید داده‌های سفارشی")
    
    try:
        choice = input("\nانتخاب کنید (1-4): ").strip()
        
        if choice == "1":
            # تولید داده‌های پیش‌فرض
            days = 30
            range_msgs = (20, 150)
            
            logger.info(f"تولید داده برای {days} روز با {range_msgs[0]}-{range_msgs[1]} پیام در روز")
            count = generate_sample_data(days, range_msgs)
            
            print(f"\n🎉 {count:,} رکورد نمونه با موفقیت تولید شد!")
            show_generated_stats()
            
        elif choice == "2":
            show_generated_stats()
            
        elif choice == "3":
            confirm = input("⚠️ آیا مطمئن هستید؟ تمام داده‌ها پاک خواهد شد (y/n): ")
            if confirm.lower() in ['y', 'yes', 'بله']:
                clear_all_data()
            else:
                print("❌ عملیات لغو شد")
                
        elif choice == "4":
            # تولید سفارشی
            try:
                days = int(input("تعداد روزها (پیش‌فرض: 30): ") or "30")
                min_msgs = int(input("حداقل پیام در روز (پیش‌فرض: 10): ") or "10")
                max_msgs = int(input("حداکثر پیام در روز (پیش‌فرض: 200): ") or "200")
                
                logger.info(f"تولید داده برای {days} روز با {min_msgs}-{max_msgs} پیام در روز")
                count = generate_sample_data(days, (min_msgs, max_msgs))
                
                print(f"\n🎉 {count:,} رکورد نمونه با موفقیت تولید شد!")
                show_generated_stats()
                
            except ValueError:
                print("❌ مقادیر نامعتبر وارد شده")
        else:
            print("❌ انتخاب نامعتبر")
            
    except KeyboardInterrupt:
        print("\n👋 خروج...")
    except Exception as e:
        logger.error(f"خطا: {e}")

if __name__ == "__main__":
    main()