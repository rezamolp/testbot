#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اجرای همزمان ربات و داشبورد آمارگیری
Run Bot and Statistics Dashboard Simultaneously
"""

import asyncio
import threading
import time
import subprocess
import signal
import sys
from telegram_auto_forward import TelegramAutoForward
import logging

# تنظیم لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BotDashboardRunner:
    """کلاس اجرای همزمان ربات و داشبورد"""
    
    def __init__(self):
        self.bot = None
        self.dashboard_process = None
        self.running = False
    
    def start_dashboard(self):
        """شروع داشبورد وب"""
        try:
            logger.info("🌐 شروع داشبورد وب...")
            # اجرای داشبورد در پروسه جداگانه
            self.dashboard_process = subprocess.Popen([
                sys.executable, 'web_dashboard.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # صبر برای اطمینان از شروع داشبورد
            time.sleep(3)
            
            if self.dashboard_process.poll() is None:
                logger.info("✅ داشبورد وب در آدرس http://localhost:5000 در حال اجرا است")
            else:
                logger.error("❌ خطا در شروع داشبورد وب")
                
        except Exception as e:
            logger.error(f"خطا در شروع داشبورد: {e}")
    
    async def start_bot(self):
        """شروع ربات تلگرام"""
        try:
            logger.info("🤖 شروع ربات تلگرام...")
            self.bot = TelegramAutoForward()
            await self.bot.start()
        except Exception as e:
            logger.error(f"خطا در اجرای ربات: {e}")
    
    def stop_dashboard(self):
        """توقف داشبورد"""
        if self.dashboard_process:
            try:
                self.dashboard_process.terminate()
                self.dashboard_process.wait(timeout=5)
                logger.info("✅ داشبورد وب متوقف شد")
            except subprocess.TimeoutExpired:
                self.dashboard_process.kill()
                logger.info("🔴 داشبورد وب به زور متوقف شد")
            except Exception as e:
                logger.error(f"خطا در توقف داشبورد: {e}")
    
    def signal_handler(self, sig, frame):
        """مدیریت سیگنال خروج"""
        logger.info("🛑 سیگنال خروج دریافت شد...")
        self.running = False
        
        # توقف داشبورد
        self.stop_dashboard()
        
        # خروج از برنامه
        sys.exit(0)
    
    async def run(self):
        """اجرای اصلی"""
        self.running = True
        
        # ثبت signal handler
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("🚀 راه‌اندازی سیستم کامل ربات اتوفوروارد با آمارگیری")
        print("=" * 60)
        
        # شروع داشبورد
        dashboard_thread = threading.Thread(target=self.start_dashboard)
        dashboard_thread.daemon = True
        dashboard_thread.start()
        
        # صبر برای شروع کامل داشبورد
        await asyncio.sleep(5)
        
        print("\n📊 داشبورد آمارگیری:")
        print("   🌐 آدرس: http://localhost:5000")
        print("   📈 نمودارهای آماری و گزارشات در دسترس است")
        
        print("\n🤖 ربات تلگرام:")
        
        # شروع ربات
        try:
            await self.start_bot()
        except KeyboardInterrupt:
            logger.info("ربات توسط کاربر متوقف شد")
        finally:
            self.stop_dashboard()

async def show_statistics_demo():
    """نمایش نمونه آمارگیری"""
    try:
        from statistics import StatisticsDB, StatisticsAnalyzer, StatisticsReporter
        
        print("\n📊 نمونه آمارگیری:")
        print("-" * 30)
        
        stats_db = StatisticsDB()
        stats_analyzer = StatisticsAnalyzer(stats_db)
        stats_reporter = StatisticsReporter(stats_db, stats_analyzer)
        
        # نمایش آمار موجود
        metrics = stats_analyzer.get_performance_metrics(30)
        if metrics:
            print(f"📈 کل پیام‌ها (30 روز): {metrics.get('total_messages', 0):,}")
            print(f"✅ نرخ موفقیت: {metrics.get('success_rate', 0)}%")
            print(f"📅 میانگین روزانه: {metrics.get('avg_messages_per_day', 0):.1f}")
        else:
            print("📭 هنوز آماری ثبت نشده است")
            print("   پس از شروع ربات، آمارها در اینجا نمایش داده می‌شود")
        
    except Exception as e:
        logger.error(f"خطا در نمایش آمار: {e}")

async def main():
    """تابع اصلی"""
    print("🎯 انتخاب نوع اجرا:")
    print("1. اجرای کامل (ربات + داشبورد)")
    print("2. فقط ربات تلگرام") 
    print("3. فقط داشبورد آمارگیری")
    print("4. نمایش آمارهای موجود")
    
    try:
        choice = input("\nانتخاب کنید (1-4): ").strip()
        
        if choice == "1":
            runner = BotDashboardRunner()
            await runner.run()
            
        elif choice == "2":
            bot = TelegramAutoForward()
            await bot.start()
            
        elif choice == "3":
            subprocess.run([sys.executable, 'web_dashboard.py'])
            
        elif choice == "4":
            await show_statistics_demo()
            
        else:
            print("❌ انتخاب نامعتبر")
            
    except KeyboardInterrupt:
        print("\n👋 خروج...")
    except Exception as e:
        logger.error(f"خطا: {e}")

if __name__ == "__main__":
    print("🔧 سیستم آمارگیری حرفه‌ای ربات تلگرام")
    print("=" * 50)
    asyncio.run(main())